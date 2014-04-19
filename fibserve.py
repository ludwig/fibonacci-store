#!/usr/bin/env python

import os, logging
from logging.handlers import RotatingFileHandler
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug import check_password_hash, generate_password_hash

app = Flask(__name__)

# Our usual configuration
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'fibserve.db'),
    SECRET_KEY = 'development key',
    DEBUG = True,
))

# Configure the flask debug toolbar
from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)
app.config.update(dict(
    DEBUG_TB_ENABLED = app.debug and False,
    #DEBUG_TB_HOSTS = ('127.0.0.1', '::1'),
    DEBUG_TB_INTERCEPT_REDIRECTS = False,
    DEBUG_TB_PROFILER_ENABLED = True,
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False,
))

# Lastly, update from environment variable
#app.config.from_envvar('FIBSERVE_SETTINGS', silent=True)

# -----------------------------------------------------------------------------

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as fp:
            db.cursor().executescript(fp.read())
        db.commit()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cursor = get_db().execute(query, args)
    rv = cursor.fetchall()
    return ((rv[0] if rv else None) if one else rv)

def get_user_id(username):
    rv = query_db("select user_id from user where username = ?", [username], one=True)
    return rv[0] if rv else None

def get_fib_pending(user_id):
    rows = query_db("select n from fibs where user_id = ? and value = ''", [user_id])
    return [row['n'] for row in rows]

def get_fib_results(user_id):
    rows = query_db("select value from fibs where user_id = ? and value <> ''", [user_id])
    return [row['value'] for row in rows]

# -----------------------------------------------------------------------------

from wtforms import Form, TextField, PasswordField, validators

class RegistrationForm(Form):

    username = TextField('Username', [
        validators.Length(min=3, max=25, message='You have to enter a username (between 3 and 25 characters)')
    ])

    email = TextField('Email Address', [
        validators.Email(message='You have to enter a valid email address')
    ])

    password = PasswordField('New Password', [
        validators.Required(message='You have to enter a password'),
        validators.EqualTo('confirm', message='The two passwords do not match')
    ])

    confirm = PasswordField('Repeat Password')

class FibonacciForm(Form):
    N = TextField('N', [validators.Regexp(r'\d+', message='Please use an integer')])

# -----------------------------------------------------------------------------

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from users where id = ?', [session['user_id']], one=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('show_fibs'));
    error = None
    if request.method == 'POST':
        user = query_db("select * from users where username = ?", [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username or password'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid username or password'
        else:
            flash('You were logged in')
            session['user_id'] = user['id']
            return redirect(url_for('show_fibs'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('show_fibs'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or ('@' not in request.form['email']):
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif not request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = get_db()
            db.execute("insert into user (username, email, pw_hash) values (?, ?, ?)",
                [request.form['username'], request.form['email'], generate_password_hash(request.form['password'])])
            db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('login'))

# -----------------------------------------------------------------------------

@app.route('/hello')
def hello_world():
    return 'Hello World!'

@app.route('/')
def show_fibs():
    results = []
    pending = []
    if g.user:
        #app.logger.info("g.user['id'] = {0!r}".format(g.user['id']))
        user_id = g.user['id']
        results = get_fib_results(user_id)
        pending = get_fib_pending(user_id)
    return render_template('show_fibs.html', results=results, pending=pending)

@app.route('/fibrequest', methods=['POST'])
def request_fib():
    if not g.user:
        # Unauthorized
        abort(401)
    if not request.form['N']:
        flash('Invalid request!')
        return redirect(url_for('show_fibs'))
    # XXX: check for xhr
    # XXX: check that N is valid
    # XXX: check if result is already in db
    # log request in database
    db = get_db()
    db.execute("insert into fibs values (?, ?, ?)", [g.user['id'], request.form['N'], ''])
    db.commit()
    # XXX: send request to celery
    return redirect(url_for('show_fibs'))
        

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    handler = RotatingFileHandler('logs/fibserve.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run()

# EOF
