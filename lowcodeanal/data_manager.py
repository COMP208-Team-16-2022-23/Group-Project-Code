# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_manager.PY
"""Manage dataset uploaded and processed"""

from flask import Blueprint, request, render_template, session, redirect

my_data = Blueprint('my_data', __name__, template_folder='Backend/templates')


@my_data.route("/my_data", methods=['GET', 'POST'])
def mydata():
    return render_template('/data_process/my_data.html')
