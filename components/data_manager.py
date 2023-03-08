# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_manager.PY
"""Manage dataset uploaded and processed"""

from flask import Blueprint, request, render_template, session, redirect, g, flash, url_for
from werkzeug.utils import secure_filename
import os
import requests

bp = Blueprint('my_data', __name__, template_folder='templates')


# define file allowance
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/my_data", methods=['GET', 'POST'])
def mydata():
    # fetch directory
    dict_files = os.listdir('temp_files')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     return redirect(url_for('download_file', name=filename))
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('temp_files', filename))
            # todo fix that cannot fetch g or session
            # a = g
            dict_files = os.listdir('temp_files')
            return render_template('dataset/my_data.html', list=dict_files)
    return render_template('dataset/my_data.html', list=dict_files)

@bp.route("/view_document", methods=['GET'])
def view_document():
    # Replace the URL with the URL of your Office document
    document_url = 'https://binaries.templates.cdn.office.net/support/templates/zh-cn/tf55871247_win32.dotx'
    # Replace the 'Office Online' string with your desired title for the viewer
    title = 'Office Online'
    # Build the HTML code for the viewer
    viewer_html = requests.get(f'https://view.officeapps.live.com/op/embed.aspx?src={document_url}').text
    return render_template('dataset/document_viewer.html', title=title, viewer_html=viewer_html)




