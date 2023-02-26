from datetime import timedelta

from flask import Flask, request, session, url_for, redirect
import os

import database as db
from blueprints.user import user_view
from blueprints.data_manager import my_data
from blueprints.data_analyse import data_analyse
# from blueprints.node_editor import node_editer

app = Flask(__name__)

# load the instance config
app.config.from_pyfile('config.py')

# todo session initialization


db.init_db()

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


# a simple page that says hello
@app.route('/hello')
def hello_world():
    return "<p>Hello, World!</p>"


app.register_blueprint(user_view)
app.register_blueprint(my_data)
app.register_blueprint(data_analyse)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.db_session.remove()


if __name__ == "__main__":
    app.run()
