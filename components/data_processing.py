from flask import Blueprint, request, render_template, session, redirect

bp = Blueprint('data_processing', __name__, url_prefix='/data_processing')


@bp.route("/", methods=['GET', 'POST'])
def data_processing():
    # todo: add logic for data processing project list and add new project button

    return render_template('data_processing/index.html')

# todo: add route for data processing project, e.g. /data_processing/project/1234567 (project id)
