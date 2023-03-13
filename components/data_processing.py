from flask import Blueprint, request, render_template, session, redirect, g, url_for

from util.storage_control import list_blobs

bp = Blueprint('data_processing', __name__, url_prefix='/data_processing')


def get_date_and_id(prefix):
    blobs_list = list_blobs(prefix=prefix)
    file_list = []
    for blob in blobs_list:
        file_list.append(
            {'file_name': blob.name.replace(prefix + '/', ""), 'date_modified': str(blob.updated).split('.')[0],
             'ID': str(blob.id).split('/')[-1]})
    return file_list


@bp.route("/", methods=['GET', 'POST'])
def data_processing():
    # todo: add logic for data processing project list and add new project button
    prefix = 'public'
    file_list = get_date_and_id(prefix)
    if g.user:
        prefix = g.user.username
        file_list += get_date_and_id(prefix)

    if request.method == 'POST':
        selected_file_id = request.form['file_selection']
        return redirect(url_for('data_processing.data_processing_project', project_id=selected_file_id))

    return render_template('data_processing/index.html', file_list=file_list)


# todo: add route for data processing project, e.g. /data_processing/project/1234567 (project id)
@bp.route("/project/<project_id>", methods=['GET', 'POST'])
def data_processing_project(project_id):
    return render_template('data_processing/project.html', project_id=project_id)
