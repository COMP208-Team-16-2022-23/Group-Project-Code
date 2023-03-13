from flask import Flask, render_template
import os
import threading
import time
from flask_mail import Mail
import database as db
from components import auth
from components import data_processing
from components import data_manager
from components import legal
from components import data_analysis
from components import file_preview
import config

# from components import node_editer

app = Flask(__name__)

# load the instance config
app.config.from_pyfile('config.py')

# initialize the mail extension
mail = Mail(app)

db.init_db()


# app.config.update(
#     GOOGLE_STORAGE_LOCAL_DEST='sandbox',
#     GOOGLE_STORAGE_SIGNATURE={"expiration": timedelta(minutes=5)},
#     GOOGLE_STORAGE_FILES_BUCKET=config.BUCKET_NAME
# )
# data_manager.storage.init_app(app)


@app.route('/')
def index():
    # use index.html as the index page
    return render_template('index.html')


app.register_blueprint(auth.bp)
app.register_blueprint(data_manager.bp)
app.register_blueprint(data_processing.bp)
app.register_blueprint(data_analysis.bp)
app.register_blueprint(file_preview.bp)
app.register_blueprint(legal.bp)

def create_temp_folder():
    # check temp_files folder is existed
    # if not, create one
    if not os.path.exists(config.TEMP_PATH):
        os.mkdir(config.TEMP_PATH)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.db_session.remove()

def run_app():
    # only set debug to True when run locally
    # do not commit debug=True
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    first_thread = threading.Thread(target=create_temp_folder)
    second_thread = threading.Thread(target=run_app)
    first_thread.start()
    second_thread.start()
