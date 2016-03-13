from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import requests
import urllib.parse as urllib
import json
import pickle

# configuration
FLASKR_SETTINGS = '/root/Bureau/hackchtx01lpw/configuration.cfg'

app = Flask(__name__)
# from_object() will look at the given object (if it’s a string it will import it) and then
# look for all uppercase variables defined there. In our case, the configuration we just wrote
# a few lines of code above. You can also move that into a separate file.
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS')


class User(object):

    def __init__(self):
        self.name = "Matthieu"

    def __str__(self):
        return self.name


class Site(object):

    def __init__(self, **kargs):
        self.name = kargs["name"]
        self.url = kargs["url"]


class Account(object):

    def __init__(self):
        url = 'http://localhost:8080/psdp/rest/auth/token'
        payload = {'grant_type': 'password',
                   'client_id': app.config['CLIENT_ID'], # 'd1f53029-9732-4d00-ba8e-0304020bef6b',
                   'client_secret': app.config['CLIENT_SECRET'], # 'secret',
                   'username': app.config['CLIENT_USERNAME'],
                   'password': app.config['CLIENT_PASSWORD']}
        headers = {'content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
        r = requests.post(url, data=urllib.urlencode(payload), headers=headers)
        if r.status_code == 200:
            self.token = json.loads(r.text)['access_token']
            self.email = app.config['CLIENT_USERNAME']

    def __init__(self, **kargs):
        self.email = kargs['email']
        self.token = kargs['token']

    def create_account(self, account):
        """
        curl -X POST --header "Content-Type: application/json" --header "Accept: application/json" --header "Authorization: Bearer 444fe5c58bf5fba921029d0e084ad7f1" -d "{
        \"name\": \"matthieu\",
        \"email\": \"m@debarre.fr\",
        \"password\": \"matthieu\"
        }" "http://localhost:8080/psdp/rest/api/user"
        :param account:
        :return int:
        """
        url = 'http://localhost:8080/psdp/rest/api/user'
        payload = {'name': account.name,
                   'email': account.email,
                   'password': account.password}
        headers = {'content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': 'Bearer '+self.token}
        r = requests.post(url, data=payload, headers=headers)
        if r.status_code == 201:
            account.id = json.loads(r.text)['id']
            return account.id
        else:
            return "ERROR"

    def delete_account(self, account_id):
        """
        :param account_id:
        :return:
        """
        pass

    def update_account(self, account_id):
        pass

    def __str__(self):
        return self.email+" et "+self.token


@app.route('/')
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('my_account'))


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    flash('New entry was successfully posted')
    return redirect(url_for('my_account'))


@app.route('/session', methods=['GET'])
def display_session():
    s = "<body>"
    if session and 'token' in session:
        s += session['token']+"<br>"
    if session and 'account' in session:
        s += str(session['account'])+"<br>"
        s += str(pickle.loads(session['account']))+"<br>"
    else:
        s += "Not Logged"
    s += "</body"
    return s


@app.route('/myaccount', methods=['GET'])
def my_account():
    if not session.get('logged_in'):
        abort(401)
    account = pickle.loads(session['account'])
    return render_template('account.html', account=account)


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
            account = Account(token=session['token'], email=request.form['username'])
            session['account'] = pickle.dumps(account)
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('my_account'))
        else:
            error = 'Unkown error'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('account', None)
    session.pop('token', None)
    flash('You were logged out')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
