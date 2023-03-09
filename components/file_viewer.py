from flask import Blueprint, render_template
from flask import send_file
import requests
import os


bp = Blueprint('file_viewer', __name__, template_folder='templates')


## embedded viewer that works
@bp.route("/view_document", methods=['GET'])
def view_document_demo():
    # Replace the URL with the URL of your Office document
    document_url = 'https://binaries.templates.cdn.office.net/support/templates/zh-cn/tf55871247_win32.dotx'
    # Replace the 'Office Online' string with your desired title for the viewer
    title = 'Office Online'
    # Build the HTML code for the viewer
    viewer_html = requests.get(f'https://view.officeapps.live.com/op/embed.aspx?src={document_url}').text
    return render_template('dataset/document_viewer.html', title=title, viewer_html=viewer_html)


## embedded viewer
## not working
@bp.route('/view_document/<path:file_path>', methods=['GET'])
def view_document(file_path='https://binaries.templates.cdn.office.net/support/templates/zh-cn/tf55871247_win32.dotx'):
    # Replace the URL with the URL of your Office document
    document_url = f'https://lcda-vgnazlwvxa-nw.a.run.app/download_file/{file_path}'
    # document_url = 'https://lcda-vgnazlwvxa-nw.a.run.app/download_file/temp_files/helloWorld.csv'
    from app import app
    document_path = os.path.join(app.root_path, file_path)
    # Replace the 'Office Online' string with your desired title for the viewer
    title = 'Document Viewer'
    # Build the HTML code for the viewer
    viewer_html = requests.get(f'https://view.officeapps.live.com/op/embed.aspx?src=file://{document_path}').text
    return render_template('dataset/document_viewer.html', title=title, viewer_html=viewer_html)


## download file
@bp.route('/download_file/<path:file_path>')
def download_file(file_path='sandbox/sample_user/hello_world.csv'):
    # Specify the file path
    
    # safety check
    #if file_path do not contain 'sandbox', return 404
    if 'sandbox' not in file_path:
        return '404'
    
    filename = file_path.split('/')[-1]
    # Send the file to the client
    return send_file(file_path, as_attachment=True, download_name=filename)
