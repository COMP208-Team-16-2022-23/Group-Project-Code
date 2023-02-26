# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:31
# @File: node_editor.PY
"""Node editor (Challenging). Handle visualizable process operation"""

from flask import Blueprint, request, render_template, session, redirect

node_editor = Blueprint('node_editor', __name__, template_folder='Backend/templates')


@node_editor.route("/nodeeditor", methods=['GET', 'POST'])
def node_editer():
    ...
