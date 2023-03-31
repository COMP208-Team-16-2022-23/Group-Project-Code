from flask import Blueprint, render_template, url_for, redirect, flash, g, request, send_file
import requests
from werkzeug.utils import secure_filename
import os
import util.storage_control as sc
import util.file_util as file
from util.models import ProcessingProject, AnalysisProject
import config
from .auth import login_required
from database import db_session

bp = Blueprint('file_preview', __name__, url_prefix='/file')


## embedded viewer demo
@bp.route("/", methods=['GET'])
def view_document_demo():
    # Replace the URL with the URL of your Office document
    # Reference: https://www.labnol.org/internet/google-docs-viewer-alternative/26591/
    document_url = 'https://www.labnol.org/files/excel.xlsx'
    # Replace the 'Office Online' string with your desired title for the viewer
    title = 'Office Online'
    # Build the HTML code for the viewer
    viewer_html = requests.get(f'https://view.officeapps.live.com/op/embed.aspx?src={document_url}').text
    return render_template('dataset/document_viewer.html', title=title, viewer_html=viewer_html)


## embedded viewer
@bp.route('/preview/<path:file_path>', methods=['GET'])
def view_document(file_path='public/hello_world.csv'):
    # Replace the URL with the URL of your Office document
    document_url = f'https://lcda-vgnazlwvxa-nw.a.run.app/file/embedded/{file_path}'

    # import urllib.parse
    # safe_document_url = urllib.parse.quote(document_url, safe='')

    # from app import app
    # document_path = os.path.join(app.root_path, file_path)
    # Replace the 'Office Online' string with your desired title for the viewer
    title = 'LCDA Document Viewer'
    # Build the HTML code for the viewer
    # viewer_html = requests.get(f'https://view.officeapps.live.com/op/embed.aspx?src={document_path}').text
    viewer_html = requests.get(f'https://view.officeapps.live.com/op/embed.aspx?src={document_url}').text

    return render_template('dataset/document_viewer.html', title=title, viewer_html=viewer_html)


'''Interfaces'''


@bp.route('/upload', methods=['POST'])
@login_required
def upload_dataset(redirect_path='my_data.my_data'):
    """
    Check limitations and upload dataset. Redirect to Login page if necessary
    :param redirect_path: Page to redirect.
    :return: Redirected page.
    """
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for(redirect_path))
    upload_file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if upload_file.filename == '':
        flash('No file selected for uploading')
        return redirect(url_for(redirect_path))

    if upload_file and g.user:
        filename = secure_filename(upload_file.filename)
        private_path = g.user.username

        # file limitations
        upload_file.seek(0, os.SEEK_END)
        file_size = upload_file.tell()
        upload_file.seek(0)

        if file_size > config.MAX_CONTENT_LENGTH:
            flash('The file you uploaded is too large')
            return redirect(url_for(redirect_path))

        root, extension = os.path.splitext(filename)
        if extension not in config.ALLOWED_EXTENSIONS:
            flash('File type not supported')
            return redirect(url_for(redirect_path))
        elif (extension == '.xlsx') or (extension == '.xls'):
            try:
                upload_file = file.xlsx_to_csv_upload(upload_file)
            except:
                flash('An error occurred while processing your file')
                return redirect(url_for(redirect_path))
            filename = root + '.csv'

        # upload file
        sc.upload_blob(upload_file, filename, prefix=private_path)
        return redirect(url_for(redirect_path))
    else:
        flash('Please log in first')
        return redirect(url_for('auth.login'))


@bp.route('/download/<path:file_path>')
def download(file_path='public/hello_world.csv'):
    """
    Download files
    :param file_path: Storage path
    :return: Download respond
    """
    # Specify the file path
    filename = file_path.split('/')[-1]
    return sc.download_with_response(file_path, filename)


@bp.route('/embedded/<path:file_path>')
def embedded_view(file_path='public/hello_world.csv'):
    # Specify the file path
    filename = file_path.split('/')[-1]
    # get the file extension
    file_extension = filename.split('.')[-1]
    file_name = filename.split('.')[0]

    # if is csv
    if file_extension == 'csv':
        filename, temp_data = sc.download_for_embedding(file_path, filename)
        temp_xlsx = file.csv_to_xlsx(filename, temp_data)

        # Send the file to the client
        return send_file(temp_xlsx, as_attachment=True, download_name=f'{file_name}.xlsx')
    else:
        return download(file_path)


@bp.route('/delete/my_data/<path:file_path>')
@login_required
def delete_dataset(file_path, force=False):
    """
    Delete datasets shown in My Data page
    :param file_path: Storage path of the file to delete
    :param force: If True, delete corresponding tasks where the dataset is in use. Otherwise, do nothing. Set to False
                  by default (Not in service)
    :return: Response of My Data page after operation
    """
    # check ownership
    owner = file_path.split('/')[0]
    if owner != g.user.username:
        flash('Deleting This File is NOT ALLOWED!')
        return redirect(url_for('my_data.my_data'))

    # delete file
    # Exists corresponding tasks
    if ProcessingProject.query.filter_by(current_file_path=file_path).first():
        # todo add alert or optimize logic
        if force:
            try:
                # delete corresponding processing task
                delete_task('data_processing', file_path)
                return redirect(url_for('my_data.my_data'))
            except Exception as e:
                print(e)

    # No corresponding task exists
    else:
        if not sc.delete_blob(file_path):
            flash('Error Occurred When Deleting File')
    return redirect(url_for('my_data.my_data'))


@bp.route('/delete/<path:component_name>/<path:file_path>')
@login_required
def delete_task(component_name, file_path):
    """
    Delete tasks shown on Processing or Analysis page
    :param component_name: Source position which calls this method
    :param file_path: Storage path of the file to delete
    :return: Response of the source position after operation
    """
    # input beyond process range or input error
    redirect_url = url_for(component_name + '.index')
    acpt_comp = ['data_processing', 'data_analysis']
    if component_name not in acpt_comp:
        return redirect(url_for('my_data.my_data'))

    # check ownership
    owner = file_path.split('/')[0]
    if owner != g.user.username:
        flash('Deleting This File is NOT ALLOWED!')
        return redirect(redirect_url)

    # Delete
    if not sc.delete_blob(file_path):
        flash('Error Occurred When Deleting File')
    else:
        # check database and delete relative row
        if component_name == 'data_processing':
            db_session.delete(ProcessingProject.query.filter_by(current_file_path=file_path).first())
            db_session.commit()
    return redirect(redirect_url)
