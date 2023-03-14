from flask import Blueprint, request, render_template, session, redirect, g, url_for

from util.storage_control import list_blobs

# database import
from database import db_session
from util.models import ProcessingProject, User

bp = Blueprint('data_processing', __name__, url_prefix='/data_processing')


def get_date_and_id(prefix):
    blobs_list = list_blobs(prefix=prefix)
    file_list = []
    for blob in blobs_list:
        file_list.append(
            {'file_name': blob.name.replace(prefix + '/', ""), 'date_modified': str(blob.updated).split('.')[0],
             'id': str(blob.id).split('/')[-1]})
    return file_list


@bp.route("/", methods=['GET', 'POST'])
def index():
    # todo: add logic for data processing project list and add new project button
    prefix = 'public'
    file_list = get_date_and_id(prefix)
    if g.user:
        prefix = g.user.username
        file_list += get_date_and_id(prefix)

    # get user's processing project list from database
    if g.user:
        processing_project_list = ProcessingProject.query.filter_by(user_id=g.user.id).all()
    else:
        processing_project_list = ProcessingProject.query.filter_by(user_id=User.query.filter(
            User.username == 'public').first().id).all()

    # logic for add new processing project
    if request.method == 'POST':
        selected_file_id = request.form['file_selection']

        # check whether the file is already in processing, if so, redirect to the processing project page
        for processing_project in processing_project_list:
            if processing_project.original_file_id == selected_file_id:
                return redirect(url_for('data_processing.project',
                                        processing_project_id=processing_project.id))

        # add new processing project to database
        # get file name from file id
        file_name = ''
        for file in file_list:
            if file['id'] == selected_file_id:
                file_name = file['file_name']
                break

        # determine whether log in
        if not g.user:
            user_id = User.query.filter(User.username == 'public').first().id
        else:
            user_id = g.user.id

        processing_project = ProcessingProject(user_id=user_id, original_file_id=selected_file_id,
                                               original_file_name=file_name)
        db_session.add(processing_project)
        db_session.commit()

        # get the latest id of the new processing project
        processing_project_id = ProcessingProject.query.filter_by(user_id=user_id, original_file_id=selected_file_id,
                                                                  original_file_name=file_name).first().id

        return redirect(url_for('data_processing.project', processing_project_id=processing_project_id))

    return render_template('data_processing/index.html', file_list=file_list,
                           processing_project_list=processing_project_list)


@bp.route("/project/<processing_project_id>", methods=['GET', 'POST'])
def project(processing_project_id):
    # todo: restrict access to the project page if the user is not the owner of the project
    return render_template('data_processing/project.html', project_id=processing_project_id)
