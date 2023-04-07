# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:31
# @File: node_editor.PY
"""Node editor (Challenging). Handle visualizable process operation"""

from flask import Blueprint, request, render_template, session, redirect

bp = Blueprint('node_editor', __name__, url_prefix='/node_editor')


@bp.route("/", methods=['GET', 'POST'])
def index():
    return render_template('node_editor/project.html')
