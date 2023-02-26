# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_analyse.PY
"""Handle data analysis process and visualization"""

from flask import Blueprint, request, render_template, session, redirect

data_analyse = Blueprint('data_analyse', __name__, template_folder='Backend/templates')


@data_analyse.route("/data_process", methods=['GET', 'POST'])
def data_process():
    ...


@data_analyse.route("/data_analysis", methods=['GET', 'POST'])
def data_analysis():
    ...
