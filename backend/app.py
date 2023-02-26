from datetime import timedelta

from flask import Flask, request, session, url_for, redirect
from blueprints.user import user_view
import os

app = Flask(__name__)
app.secret_key = 'abctest'

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'dataflow.mysql'),  # the database file
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=45)
)

# load the instance config, if it exists, when not testing
app.config.from_pyfile('config.py', silent=True)

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

if __name__ == "__main__":
    app.run()
