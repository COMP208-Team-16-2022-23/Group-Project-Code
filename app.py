from flask import Flask, render_template
import os

import database as db
from components import auth

from datetime import timedelta
from flask_mail import Mail
from flask_googlestorage import GoogleStorage, Bucket
import config

from components import data_manager
from components import legal
from components import data_analyse
from components import file_viewer

# from components import node_editer

app = Flask(__name__)

# load the instance config
app.config.from_pyfile('config.py')

# initialize the mail extension
mail = Mail(app)

# initialize the storage client
files = Bucket(config.BUCKET_NAME)
storage = GoogleStorage(files)

app.config.update(
    GOOGLE_STORAGE_LOCAL_DEST=app.instance_path,
    GOOGLE_STORAGE_SIGNATURE={"expiration": timedelta(minutes=5)},
    GOOGLE_STORAGE_FILES_BUCKET=config.BUCKET_NAME
)

db.init_db()


# storage.init_app(app)


@app.route('/')
def index():
    # use index.html as the index page
    return render_template('index.html')


app.register_blueprint(auth.bp)
app.register_blueprint(data_manager.bp)
app.register_blueprint(legal.bp)
app.register_blueprint(data_analyse.bp)
app.register_blueprint(file_viewer.bp)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.db_session.remove()


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
