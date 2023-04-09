# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:31
# @File: node_editor.PY
"""Node editor (Challenging). Handle visualizable process operation"""

from flask import Blueprint, request, render_template, session, redirect, url_for
import json
import html
import config

from util.storage_control import list_blobs, upload_blob
from algorithms import data_proc

bp = Blueprint('node_editor', __name__, url_prefix='/node_editor')


@bp.route("/", methods=['GET', 'POST'])
def index():
    datasets = list_blobs(prefix='public', ext_filter=config.ALLOWED_EXTENSIONS)
    with open('algorithms/data_proc_para_cfg.json', 'r') as f:
        processing_cfg = json.load(f)

    datasets = json.dumps(datasets)
    processing_cfg = json.dumps(processing_cfg)

    return render_template('node_editor/project.html', my_data=datasets, processing_cfg=processing_cfg)


@bp.route("/processing", methods=['GET', 'POST'])
def processing():
    result_path = ''
    input_path = 'public/CW_Data.csv'
    if request.method == 'POST':
        column_selected = request.form.getlist('column_selected')
        column_selected = column_selected[0].split(',')
        algorithm_config = request.form.to_dict()
        algorithm_config["column_selected"] = column_selected
        result_path = algorithm_config.pop('result_path')
        print('paras:', algorithm_config)

        result_path = data_proc.process(input_path, algorithm_config, result_path)

    # update the database
    # processing_project.current_file_path = processed_file_path
    # processing_project.modified_date = datetime.datetime.utcnow()
    # db_session.commit()

    # refresh the page
    # return redirect(url_for('data_processing.project', processing_project_id=processing_project_id))

    return result_path
