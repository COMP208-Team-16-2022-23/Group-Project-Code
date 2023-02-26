from datetime import timedelta

from flask import Flask, request, session, url_for, redirect
from blueprints.user import user_view
import os

import database as db
from blueprints.user import user_view

app = Flask(__name__)

# load the instance config
app.config.from_pyfile('config.py', silent=True)

# todo session initialization

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'dataflow.mysql'),  # the database file
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=45)
)

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


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.db_session.remove()


if __name__ == "__main__":
    app.run()
