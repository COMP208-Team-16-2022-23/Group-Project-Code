from flask import Flask, render_template
import os

import database as db
from components import auth

from flask_mail import Mail

from components import data_manager
# from . import data_analyse
# from blueprints.node_editor import node_editer

app = Flask(__name__)

# load the instance config
app.config.from_pyfile('config.py')

# initialize the mail extension
mail = Mail(app)

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


@app.route('/')
def index():
    # use index.html as the index page
    return render_template('index.html')


app.register_blueprint(auth.bp)
app.register_blueprint(data_manager.bp)
# app.register_blueprint(data_analyse)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.db_session.remove()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
