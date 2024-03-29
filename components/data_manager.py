# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_manager.PY
"""Manage dataset uploaded and processed"""
import json
import os
from flask import Blueprint, request, render_template, session, redirect, g, flash, url_for
import config
from util.file_util import xlsx_to_csv_upload
from util.storage_control import list_blobs, list_blobs_names, upload_blob, delete_blob

bp = Blueprint('my_data', __name__, url_prefix='/my_data')

# define file allowance
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

try:
    config_dict = json.loads(os.environ.get('CONFIG'))
    bucket_name = config_dict['BUCKET_NAME']
except:
    import secret
    bucket_name = secret.BUCKET_NAME



@bp.route("/", methods=['GET', 'POST'])
def my_data():
    private_files = []
    public_files = list_blobs(bucket_name, 'public', ext_filter=config.ALLOWED_EXTENSIONS)
    if g.user:
        private_path = g.user.username
        private_files = list_blobs(bucket_name, private_path, ext_filter=config.ALLOWED_EXTENSIONS)
    dict_files = public_files + private_files

    return render_template('dataset/my_data.html', list=dict_files)
