# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_manager.PY
"""Manage dataset uploaded and processed"""

from flask import Blueprint, request, render_template, session, redirect, g, flash, url_for
from werkzeug.utils import secure_filename
import config
from util.storage_control import list_blobs_names, upload_blob, delete_blob

bp = Blueprint('my_data', __name__, url_prefix='/my_data')

# define file allowance
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/", methods=['GET', 'POST'])
def my_data():
    private_files = []
    bucket_name = config.BUCKET_NAME
    public_files = list_blobs_names(bucket_name, 'public')
    if g.user:
        private_path = g.user.username
        private_files = list_blobs_names(bucket_name, private_path)
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
            flash('No selected file')
            return redirect(request.url)
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     return redirect(url_for('download_file', name=filename))
        if file and g.user:
            filename = secure_filename(file.filename)
            upload_blob(file, filename, prefix=private_path)
            dict_files = list_blobs_names(prefix=private_path) + public_files
            return render_template('dataset/my_data.html', list=dict_files)
    return render_template('dataset/my_data.html', list=dict_files)
