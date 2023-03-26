# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_analyse.PY
"""Handle data analysis process and visualization"""

from flask import Blueprint, request, render_template, session, redirect
import os

bp = Blueprint('data_analysis', __name__, url_prefix='/data_analysis')


@bp.route("/", methods=['GET', 'POST'])
def data_analysis():
    # TODO: Similar interface as data_processing
    dict_files = os.listdir('misc/temp')
    return render_template('dataset/data_analysis.html')
