# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_analyse.PY
"""Handle data analysis process and visualization"""

from flask import Blueprint, request, render_template, session, redirect
import os

bp = Blueprint('data_analyse', __name__, template_folder='templates')


@bp.route("/data_process", methods=['GET', 'POST'])
def data_process():
    dict_files = os.listdir('temp_files')
    return render_template('dataset/data_process.html', list=dict_files)


@bp.route("/data_analysis", methods=['GET', 'POST'])
def data_analysis():
    ...
