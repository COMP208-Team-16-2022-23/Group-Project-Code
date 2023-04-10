from flask import Flask, render_template
import os
from flask_mail import Mail
import database as db
from components import auth
from components import data_processing
from components import data_manager
from components import legal
from components import data_analysis
from components import file_preview
from components import chatgpt
from components import node_editor
from components import forum
import json
import config


app = Flask(__name__)

try:
    # Get configuration from system variables
    config_str = os.environ.get('CONFIG')
    config_dict = json.loads(config_str)
    app.config.update(config_dict)
except:
    # load the instance config
    import secret
    app.config.from_pyfile('secret.py')

# initialize the mail extension
mail = Mail(app)

db.init_db()


@app.route('/')
def index():
    # use index.html as the index page
    return render_template('index.html')


@app.context_processor
def inject_():
    try:
        maintenance_json = os.environ.get('MAINTENANCE')
        maintenance = json.loads(maintenance_json)
        MAINTENANCE_MESSAGE = maintenance['MAINTENANCE_MESSAGE']
        MAINTENANCE_TITLE = maintenance['MAINTENANCE_TITLE']
    except:
        MAINTENANCE_MESSAGE = config.MAINTENANCE_MESSAGE
        MAINTENANCE_TITLE = config.MAINTENANCE_TITLE

    return {
        'DOMAIN_NAME': app.config['DOMAIN'],
        'MAINTENANCE_MESSAGE': MAINTENANCE_MESSAGE,
        'MAINTENANCE_TITLE': MAINTENANCE_TITLE,
    }


app.register_blueprint(auth.bp)
app.register_blueprint(data_manager.bp)
app.register_blueprint(data_processing.bp)
app.register_blueprint(data_analysis.bp)
app.register_blueprint(file_preview.bp)
app.register_blueprint(legal.bp)
app.register_blueprint(chatgpt.bp)
app.register_blueprint(node_editor.bp)
app.register_blueprint(forum.bp)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.db_session.remove()


def run_app():
    # only set debug to True when run locally
    # do not commit debug=True
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


if __name__ == "__main__":
    run_app()
