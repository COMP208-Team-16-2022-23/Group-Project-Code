# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_manager.PY
"""Manage dataset uploaded and processed"""

from flask import Blueprint, request, render_template, session, redirect

data_manager = Blueprint('data_manager', __name__, template_folder='Backend/templates')


@data_manager.route("/mydata", methods=['GET', 'POST'])
def mydata():
    ...
