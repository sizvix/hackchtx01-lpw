from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import requests

# configuration
#export FLASKR_SETTINGS = '/root/Bureau/hackchtx01-lpw/configuration.cfg'

app = Flask(__name__)
# from_object() will look at the given object (if it’s a string it will import it) and then
# look for all uppercase variables defined there. In our case, the configuration we just wrote
# a few lines of code above. You can also move that into a separate file.
#app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS')


@app.route('/')
def show_entries():
    r = requests.get("http://www.instructables.com")

    r.text
    status=r.status_code,
    content_type=r.headers['content-type'],

    entries = [{"title": "titre1", "text": r.text}, {"title": "titre2", "text": r.text}]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
