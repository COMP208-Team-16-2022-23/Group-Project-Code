# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_analyse.PY
"""Handle data analysis process and visualization"""
import pandas as pd
from flask import Blueprint, request, flash, redirect, url_for, render_template, g
from util import storage_control

from components.auth import login_required
from util.models import AnalysisProject, User, AnalysisResult
from database import db_session

from algorithms import data_anal

bp = Blueprint('data_analysis', __name__, url_prefix='/data_analysis')


@bp.route("/", methods=['GET', 'POST'])
def index():
    # TODO: Similar interface as data_processing
    prefix = 'public'
    file_list = storage_control.list_blobs(prefix=prefix)
    if g.user:
        prefix = g.user.username
        file_list += storage_control.list_blobs(prefix=prefix)

    # get user's processing project list from database
    if g.user:
        analysis_project_list = AnalysisProject.query.filter_by(user_id=g.user.id).all()
    else:
        analysis_project_list = AnalysisProject.query.filter_by(user_id=User.query.filter(
            User.username == 'public').first().id).all()

    if request.method == 'POST':
        if not g.user:
            flash('Please log in first')
            return redirect(url_for('auth.login'))

        selected_file_path = request.form['file_selection']

        # check whether the file is already in processing, if so, redirect to the processing project page
        for analysis_project in analysis_project_list:
            if analysis_project.original_file_path == selected_file_path:
                return redirect(url_for('data_analysis.project', analysis_project_id=analysis_project.id))

        # add new processing project to database
        user_id = g.user.id

        analysis_project = AnalysisProject(user_id=user_id, original_file_path=selected_file_path)
        db_session.add(analysis_project)
        db_session.commit()

        # get the latest id of the new processing project
        analysis_project_id = AnalysisProject.query.filter_by(user_id=user_id,
                                                              original_file_path=selected_file_path).first().id

        return redirect(url_for('data_analysis.project', analysis_project_id=analysis_project_id))

    return render_template('data_analysis/index.html', analysis_project_list=analysis_project_list, file_list=file_list)


@bp.route("/project/<analysis_project_id>", methods=['GET', 'POST'])
@login_required
def project(analysis_project_id):
    analysis_project = AnalysisProject.query.filter_by(id=analysis_project_id).first()
    if analysis_project is None:
        flash(f'Error: Analysis project {analysis_project_id} does not exist')
        return redirect(url_for('data_analysis.index'))

    if analysis_project.user_id != g.user.id:
        flash('Error: You do not have access to this project')
        return redirect(url_for('data_analysis.index'))

    file_name = analysis_project.original_file_path.split('/')[-1]

    # get column names from the file
    file_data = storage_control.download_to_memory(analysis_project.original_file_path)
    if file_data is None:
        flash(f'Error: Cannot download file {analysis_project.original_file_path}')
        return redirect(url_for('data_analysis.index'))
    df = pd.read_csv(file_data)
    column_names = df.columns

    # read algorithm list from json file
    import os
    import json
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(parent_dir, 'algorithms', 'data_anal_para_cfg.json')
    with open(file_path, 'r') as f:
        data_analysis_algorithms_config = json.load(f)

    # get the result file path from database
    results = []
    analysis_results = AnalysisResult.query.filter_by(project_id=analysis_project_id).all()
    for analysis_result in analysis_results:
        # read the result file in .json format
        results.append(json.load(storage_control.download_to_memory(analysis_result.result_file_path)))
        # for local test
        # print(results[-1])

    if request.method == 'POST':
        # get selected function name
        function_name = request.form['function_name']

        # find varaible names of the selected function in the json file
        variable_name = ''
        for section in data_analysis_algorithms_config:
            for algorithm in section['algorithms']:
                if algorithm['code_name'] == function_name:
                    for variable in algorithm['variables']:
                        if variable['type'] == 'multi_select':
                            variable_name = variable['name']

        column_selected = request.form.getlist(variable_name)
        algorithm_config = request.form.to_dict()
        algorithm_config[variable_name] = column_selected

        # for local test
        # print(algorithm_config)

        # # for local test
        # result_file_path = data_anal.analysis(file_path=analysis_project.original_file_path,
        #                                       parameters=algorithm_config)

        # for shipping to server
        try:
            result_file_path = data_anal.analysis(file_path=analysis_project.original_file_path,
                                                  parameters=algorithm_config)
        except Exception as e:
            flash(f'Error: {e}')
            return redirect(url_for('data_analysis.project', analysis_project_id=analysis_project_id))

        # update the result database
        # first check whether the result is already in the database, if so, redirect to the processing project page
        # if not, add the result to the database
        analysis_result = AnalysisResult.query.filter_by(project_id=analysis_project_id,
                                                         result_file_path=result_file_path).first()
        if analysis_result is None:
            analysis_result = AnalysisResult(project_id=analysis_project_id, result_file_path=result_file_path)
            db_session.add(analysis_result)
            db_session.commit()
        return redirect(url_for('data_analysis.project', analysis_project_id=analysis_project_id))

    return render_template('data_analysis/project.html', project_id=analysis_project_id, file_name=file_name,
                           column_names=column_names, data_analysis_algorithms=data_analysis_algorithms_config,
                           results=results)
