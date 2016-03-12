from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import requests
import urllib.parse as urllib
import json
import pickle

# configuration
#export FLASKR_SETTINGS = '/root/Bureau/hackchtx01-lpw/configuration.cfg'

app = Flask(__name__)
# from_object() will look at the given object (if it’s a string it will import it) and then
# look for all uppercase variables defined there. In our case, the configuration we just wrote
# a few lines of code above. You can also move that into a separate file.
#app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS')


class User(object):

    def __init__(self, token):
        self.name = "Matthieu"
        self.token = token

    def __str__(self):
        return self.name+" et "+self.token


@app.route('/')
def show_entries():
    entries=[
        {"title": "titre1", "text": 'a'},
        {"title": "titre2", "text": 'a'}
    ]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/session', methods=['GET'])
def display_session():
    s = "<body>"
    if session and session['token']:
        s += session['token']+"<br>"
    if session and session['user']:
        s += str(session['user'])+"<br>"
        s += str(pickle.loads(session['user']))+"<br>"
    else:
        s += "Not Logged"
    s += "</body"
    return s


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        url = 'http://localhost:8080/psdp/rest/auth/token'
        payload = {'grant_type': 'password',
                   'client_id': app.config['CLIENT_ID'], # 'd1f53029-9732-4d00-ba8e-0304020bef6b',
                   'client_secret': app.config['CLIENT_SECRET'], # 'secret',
                   'username': request.form['username'],
                   'password': request.form['password']}
        headers = {'content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
        r = requests.post(url, data=urllib.urlencode(payload), headers=headers)
        print(r.status_code)
        if r.status_code == 401:
            error = 'Invalid password'
        elif r.status_code == 200:
            session['token'] = json.loads(r.text)['access_token']
            user = User(session['token'])
            session['user'] = pickle.dumps(user)
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
        else:
            error = 'Unkown error'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    session.pop('token', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
