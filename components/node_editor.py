# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:31
# @File: node_editor.PY
"""Node editor (Challenging). Handle visualizable process operation"""

from flask import Blueprint, request, render_template, g, redirect, url_for
import json

import pandas

import config
from util.storage_control import list_blobs, upload_blob, download_to_memory
from util.file_util import add_suffix
from algorithms import data_proc

bp = Blueprint('node_editor', __name__, url_prefix='/node_editor')


@bp.route("/", methods=['GET', 'POST'])
def index():
    datasets = list_blobs(prefix='public', ext_filter=config.ALLOWED_EXTENSIONS)
    with open('algorithms/data_proc_para_cfg.json', 'r') as f:
        processing_cfg = json.load(f)

    for dataset in datasets:
        df = pandas.read_csv(download_to_memory(dataset['file_path']))
        column_list = list(df.columns.values)
        column_info = {'columns': column_list}
        dataset.update(column_info)

    datasets = json.dumps(datasets)
    processing_cfg = json.dumps(processing_cfg)

    return render_template('node_editor/project.html', my_data=datasets, processing_cfg=processing_cfg)


@bp.route("/processing", methods=['GET', 'POST'])
def processing():
    result_path = ''
    input_path = ''
    if request.method == 'POST':
        payload = request.get_json()
        column_selected = payload['column_selected']
        algorithm_config = payload
        algorithm_config["column_selected"] = column_selected.split(',')
        input_path = algorithm_config.pop('file_path')
        result_path = algorithm_config.pop('result_path')
        result_path = add_suffix(result_path, '', g.user.username, 'node_editor')
        print('paras:', algorithm_config)

        result_path = data_proc.process(input_path, algorithm_config, result_path)

    # update the database
    # processing_project.current_file_path = processed_file_path
    # processing_project.modified_date = datetime.datetime.utcnow()
    # db_session.commit()

    # refresh the page
    # return redirect(url_for('data_processing.project', processing_project_id=processing_project_id))

    return json.dumps({'success':True, 'payload': result_path}), 200, {'ContentType': 'application/json'}
