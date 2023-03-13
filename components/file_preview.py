from flask import Blueprint, render_template
from flask import send_file
import requests
import os
import util.file_manager as fmgr
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

    # safety check
    # if file_path do not contain 'sandbox', return 404
    # if 'sandbox' not in file_path:
    #     return '404'

    filename = file_path.split('/')[-1]
    return fmgr.download_with_response(file_path, filename)
    # temp_file = f'temp_files/{filename}'
    # download_blob(file_path, temp_file, BUCKET_NAME)

    # Send the file to the client
    # return send_file(temp_file, as_attachment=True, download_name=filename)


@bp.route('/embedded/<path:file_path>')
def embedded_view(file_path='public/hello_world.csv'):
    # Specify the file path
    filename = file_path.split('/')[-1]
    # get the file extension
    file_extension = filename.split('.')[-1]
    file_name = filename.split('.')[0]
    temp_file = f'{config.TEMP_PATH}/{filename}'

    #if is csv
    if file_extension == 'csv':
        filename, temp_name = fmgr.download_for_embedding(file_path, filename)
        temp_path_xlsx = file.csv_to_xlsx(filename, temp_name)
        # temp_file = f'{config.TEMP_PATH}/{temp_name_xlsx}'

        # Send the file to the client
        return send_file(temp_path_xlsx, as_attachment=True, download_name=f'{file_name}.xlsx')
    else:
        return download(file_path)

###
