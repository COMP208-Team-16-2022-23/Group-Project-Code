import datetime

import pandas
from flask import Blueprint, request, render_template, session, redirect, g, url_for, flash

import config
from util.storage_control import list_blobs, download_to_memory, copy_to_username
from algorithms import data_proc

# database import
from database import db_session
from util.models import ProcessingProject, User
from components.auth import login_required

bp = Blueprint('data_processing', __name__, url_prefix='/data_processing')


@bp.route("/", methods=['GET', 'POST'])
def index():
    prefix = 'public'
    file_list = list_blobs(prefix=prefix, ext_filter=config.ALLOWED_EXTENSIONS)
    if g.user:
        prefix = g.user.username
        file_list += list_blobs(prefix=prefix, ext_filter=config.ALLOWED_EXTENSIONS)

    # get user's processing project list from database
    if g.user:
        processing_project_list = ProcessingProject.query.filter_by(user_id=g.user.id).all()
    else:
        processing_project_list = ProcessingProject.query.filter_by(user_id=User.query.filter(
            User.username == 'public').first().id).all()

    # logic for add new processing project
    if request.method == 'POST':
        if not g.user:
            flash('Please log in first', 'warning-auth')
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))

        selected_file_path = request.form['file_selection']

        # check whether the file is already in processing, if so, redirect to the processing project page
        for processing_project in processing_project_list:
            if processing_project.original_file_path == selected_file_path:
                return redirect(url_for('data_processing.project', processing_project_id=processing_project.id))

        # add new processing project to database
        user_id = g.user.id

        copied_file_path = copy_to_username(file_path=selected_file_path, username=g.user.username)

        processing_project = ProcessingProject(user_id=user_id, original_file_path=selected_file_path,
                                               current_file_path=copied_file_path)
        db_session.add(processing_project)
        db_session.commit()

        # get the latest id of the new processing project
        processing_project_id = ProcessingProject.query.filter_by(user_id=user_id,
                                                                  original_file_path=selected_file_path).first().id

        return redirect(url_for('data_processing.project', processing_project_id=processing_project_id))

    return render_template('data_processing/index.html', file_list=file_list,
                           processing_project_list=processing_project_list,
                           button_status="disabled" if g.user is None else "")


@bp.route("/project/<processing_project_id>", methods=['GET', 'POST'])
@login_required
def project(processing_project_id):
    # todo: restrict access to the project page if the user is not the owner of the project

    # get blob from processing project id
    processing_project = ProcessingProject.query.filter_by(id=processing_project_id).first()
    if processing_project is None:
        flash(f'Error: Processing project {processing_project_id} does not exist')
        return redirect(url_for('data_processing.index'))

    if processing_project.user_id != g.user.id:
        flash('Error: You do not have access to this project')
        return redirect(url_for('data_processing.index'))

    # get column names from the file
    df = pandas.read_csv(download_to_memory(processing_project.current_file_path))
    column_names = list(df.columns)

    # read algorithm list from json file in ../algorithm/data_processing_algorithm_config.json
    import os
    import json
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(parent_dir, 'algorithms', 'data_proc_para_cfg.json')
    with open(file_path, 'r') as f:
        data_processing_algorithms_config = json.load(f)

    # logic for processing
    if request.method == 'POST':
        column_selected = request.form.getlist('column_selected')
        algorithm_config = request.form.to_dict()
        algorithm_config["column_selected"] = column_selected

        try:
            processed_file_path = data_proc.process(processing_project.current_file_path, algorithm_config)
        except Exception as e:
            flash('Error: ' + str(e))
            return redirect(url_for('data_processing.project', processing_project_id=processing_project_id))

        # update the database
        processing_project.current_file_path = processed_file_path
        processing_project.modified_date = datetime.datetime.utcnow()
        db_session.commit()

        # refresh the page
        return redirect(url_for('data_processing.project', processing_project_id=processing_project_id))

    return render_template('data_processing/project.html', project_id=processing_project_id,
                           file_path=processing_project.current_file_path,
                           column_names=column_names,
                           data_processing_algorithms=data_processing_algorithms_config)
