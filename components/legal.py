# -*- coding = utf-8 -*-
# @Time: 2023/2/26 11:21
# @File: data_manager.PY
"""Manage dataset uploaded and processed"""

from flask import Blueprint, request, render_template
from werkzeug.utils import secure_filename
import os

bp = Blueprint('legal', __name__, url_prefix='/legal')


@bp.route("/terms", methods=['GET'])
def terms():
    return render_template('legal/terms.html')


@bp.route("/privacy", methods=['GET'])
def privacy():
    return render_template('legal/privacy.html')
