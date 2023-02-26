from flask import Flask, request, session, url_for, redirect

app = Flask(__name__)
app.secret_key = 'abctest'
# todo session initialization


@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        # return index template
        return 'Logged in as ' + username + '<br>' + \
         "<b><a href = '/logout'>click here to log out</a></b>"
    return "You are not logged in <br><a href = '/login'></b>" + \
      "click here to log in</b></a>"


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    # return login page template
    return '''
       <form action = "" method = "post">
          <p><input type = text name = username/></p>
          <p><input type = submit value = Login></p>
       </form>

       '''


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/mydata", methods=['GET', 'POST'])
def mydata():
    ...


@app.route("/dataprocess", methods=['GET', 'POST'])
def dataprocess():
    ...


@app.route("/dataanalysis", methods=['GET', 'POST'])
def dataanalysis():
    ...


@app.route("/nodeeditor", methods=['GET', 'POST'])
def nodeediter():
    ...


if __name__ == "__main__":
    app.run()
