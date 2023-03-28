# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_manager.PY
"""Manage dataset uploaded and processed"""

from flask import Blueprint, request, render_template, session, redirect, g, flash, url_for
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


    return render_template('dataset/my_data.html', list=dict_files)
