from flask import Flask, render_template
import os
from flask_mail import Mail
import database as db
from components import auth
from components import data_processing
from components import data_manager
from components import legal
from components import data_analysis
from components import file_viewer

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
app.register_blueprint(file_viewer.bp)
app.register_blueprint(legal.bp)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.db_session.remove()


if __name__ == "__main__":
    # only set debug to True when run locally
    # do not commit debug=True
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
