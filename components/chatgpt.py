from flask import Flask, request, jsonify, Blueprint, render_template

bp = Blueprint('chatgpt', __name__, url_prefix='/chat')


@bp.route('/')
def index():
    return render_template('dataset/chat.html')


@bp.route("/send", methods=["POST"])
def send_message():
    from util.gpt import generate_response
    prompt = request.form['message']
    response = generate_response(prompt)
    return response


