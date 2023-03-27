from flask import Blueprint, render_template, url_for, redirect, flash, g
from flask import send_file
import requests
import os
import util.storage_control as sc
import util.file_util as file
import config

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


## download file
@bp.route('/download/<path:file_path>')
def download(file_path='public/hello_world.csv'):
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

    #if is csv
    if file_extension == 'csv':
        filename, temp_data = sc.download_for_embedding(file_path, filename)
        temp_xlsx = file.csv_to_xlsx(filename, temp_data)

        # Send the file to the client
        return send_file(temp_xlsx, as_attachment=True, download_name=f'{file_name}.xlsx')
    else:
        return download(file_path)


@bp.route('/delete/my_data/<path:file_path>')
def delete_dataset(file_path):
    owner = file_path.split('/')[0]
    if owner != g.user.username:
        flash('Deleting This File is NOT ALLOWED!')
        return redirect(url_for('my_data.my_data'))
    if not sc.delete_blob(file_path):
        flash('Error Occur When Deleting File')
    return redirect(url_for('my_data.my_data'))
