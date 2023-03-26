# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_manager.PY
"""Manage dataset uploaded and processed"""

from flask import Blueprint, request, render_template, session, redirect, g, flash, url_for
from werkzeug.utils import secure_filename
import config
from util.file_util import xlsx_to_csv_upload
from util.storage_control import list_blobs, list_blobs_names, upload_blob, delete_blob

bp = Blueprint('my_data', __name__, url_prefix='/my_data')

# define file allowance
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/", methods=['GET', 'POST'])
def my_data():
    private_files = []
    bucket_name = config.BUCKET_NAME
    public_files = list_blobs(bucket_name, 'public')
    if g.user:
        private_path = g.user.username
        private_files = list_blobs(bucket_name, private_path)
    dict_files = public_files + private_files
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     return redirect(url_for('download_file', name=filename))
        if file and g.user:
            filename = secure_filename(file.filename)
            # check the size of the file
            if file.content_length > config.MAX_CONTENT_LENGTH:
                flash('The file you uploaded is too large')
                return redirect(request.url)
            if filename.split('.')[-1] == 'csv':
                pass
            elif (filename.split('.')[-1] == 'xlsx') or (filename.split('.')[-1] == 'xls'):
                # TODO: fix the bug that the file is not saved
                try:
                    file = xlsx_to_csv_upload(file)
                except:
                    flash('An error occurred while processing your file')
                filename = filename.split('.')[0] + '.csv'
            else:
                flash('File type not supported')
                return redirect(request.url)
            upload_blob(file, filename, prefix=private_path)
            dict_files = list_blobs(prefix=private_path) + public_files
            return render_template('dataset/my_data.html', list=dict_files)
        else:
            flash('Please log in first')
            return redirect(url_for('auth.login'))

    return render_template('dataset/my_data.html', list=dict_files)
