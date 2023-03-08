from flask import Blueprint, render_template
from flask import send_file
import requests

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
    document_url = f'https://lcda-vgnazlwvxa-nw.a.run.app/download_csv/{file_path}'
    # document_url = 'https://lcda-vgnazlwvxa-nw.a.run.app/download_csv/temp_files/helloWorld.csv'
    # Replace the 'Office Online' string with your desired title for the viewer
    title = 'Document Viewer'
    # Build the HTML code for the viewer
    viewer_html = requests.get(f'https://view.officeapps.live.com/op/embed.aspx?src={document_url}').text
    return render_template('dataset/document_viewer.html', title=title, viewer_html=viewer_html)


## download file
@bp.route('/download_csv/<path:file_path>')
def download_file(file_path='temp_files/helloWorld.csv'):
    # Specify the file path
    filename = file_path.split('/')[-1]
    # Send the file to the client
    return send_file(file_path, as_attachment=True, download_name=filename)


