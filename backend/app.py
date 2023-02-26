from flask import Flask, request, session, url_for, redirect
from blueprints.user import user_view


app = Flask(__name__)
app.secret_key = 'abctest'
# todo session initialization

app.register_blueprint(user_view)


if __name__ == "__main__":
    app.run()
