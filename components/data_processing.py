import pandas
from flask import Blueprint, request, render_template, session, redirect, g, url_for

from util.storage_control import list_blobs, download_to_memory
from algorithms import data_proc

# database import
from database import db_session
from util.models import ProcessingProject, User

bp = Blueprint('data_processing', __name__, url_prefix='/data_processing')


@bp.route("/", methods=['GET', 'POST'])
def index():
    # todo: add logic for data processing project list and add new project button
    prefix = 'public'
    file_list = list_blobs(prefix=prefix)
    if g.user:
        prefix = g.user.username
        file_list += list_blobs(prefix=prefix)

    # get user's processing project list from database
    if g.user:
        processing_project_list = ProcessingProject.query.filter_by(user_id=g.user.id).all()
    else:
        processing_project_list = ProcessingProject.query.filter_by(user_id=User.query.filter(
            User.username == 'public').first().id).all()

    # logic for add new processing project
    if request.method == 'POST':
        selected_file_path = request.form['file_selection']

        # check whether the file is already in processing, if so, redirect to the processing project page
        for processing_project in processing_project_list:
            if processing_project.original_file_path == selected_file_path:
                return redirect(url_for('data_processing.project', processing_project_id=processing_project.id))

        # add new processing project to database

        # determine whether log in
        if not g.user:
            user_id = User.query.filter(User.username == 'public').first().id
        else:
            user_id = g.user.id

        processing_project = ProcessingProject(user_id=user_id, original_file_path=selected_file_path)
        db_session.add(processing_project)
        db_session.commit()

        # get the latest id of the new processing project
        processing_project_id = ProcessingProject.query.filter_by(user_id=user_id,
                                                                  original_file_path=selected_file_path, ).first().id

        return redirect(url_for('data_processing.project', processing_project_id=processing_project_id))

    # for file in file_list:
    #     file['file_name'] = remove_prefix(file['file_name'])
    #
    # for processing_project in processing_project_list:
    #     processing_project.original_file_name = remove_prefix(processing_project.original_file_name)

    return render_template('data_processing/index.html', file_list=file_list,
                           processing_project_list=processing_project_list)


@bp.route("/project/<processing_project_id>", methods=['GET', 'POST'])
def project(processing_project_id):
    # todo: restrict access to the project page if the user is not the owner of the project

    # get blob from processing project id
    processing_project = ProcessingProject.query.filter_by(id=processing_project_id).first()
    if processing_project is None:
        return redirect(url_for('data_processing.index'))

    # read algorithm list from json file in ../algorithm/data_processing_algorithm_config.json
    import os
    import json
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(parent_dir, 'algorithms', 'data_proc_para_cfg.json')
    with open(file_path, 'r') as f:
        data_processing_algorithms_config = json.load(f)

    if request.method == 'POST':
        algorithm_config = request.form.to_dict()
        # print(algorithm_config)
        # get the algorithm name from the form
        algorithm_name = request.form['function_name']
        # get the algorithm config from the form
        algorithm_config.pop('function_name')
        algorithm_paras = list(algorithm_config.values())
        # add the algorithm to the processing project
        file = pandas.read_csv(download_to_memory(processing_project.current_file_path))
        # print(list(algorithm_config.values()))
        print(data_proc.value_replace_mean(file, algorithm_paras))
        # # update the database
        # db_session.commit()
        #
        # # redirect to the project page
        # return redirect(url_for('data_processing.project', processing_project_id=processing_project_id))

    return render_template('data_processing/project.html', project_id=processing_project_id,
                           file_path=processing_project.current_file_path,
                           data_processing_algorithms=data_processing_algorithms_config)
