#!/usr/bin/env python
# See http://flask-script.readthedocs.org/en/latest/

import os, sys
import pprint
from flask import Flask, current_app
from flask.ext.script import Manager, Server, Shell, prompt_bool
from fibserve import app

# XXX: figure out how to change configs here
def create_app(config=None):
    app = Flask(__name__)
    if config is not None:
        app.config.from_pyfile(config)
    # configure your app
    return app

# Use app factory function to create the manager
#manager = Manager(create_app)

# Use our fibserve.app to create the manager
manager = Manager(app)

# We can optionally specify a config file for our server (for dev, test, prod, ...)
# This option is useful when we create the manager using an app factory function.
manager.add_option('-c', '--config', dest='config', required=False)

# Server runs on port 5000 by default. Change it here.
manager.add_command("runserver", Server(port=5000))

# Start shell with everything we need (to avoid importing same stuff all the time)
def _shell_context_factory():
    return dict(app=app, os=os, sys=sys, pprint=pprint)
manager.add_command("shell", Shell(make_context=_shell_context_factory))

@manager.command
def dumpconfig():
    """Dumps config"""
    from fibserve import app
    pprint.pprint(app.config.copy())

@manager.command
def initdb():
    """Initializes database"""
    from fibserve import init_db
    if prompt_bool('Are you sure you want to reinitialize your database?'):
        init_db()

@manager.command
def generate_password_hash():
    """Generates password hash"""
    from werkzeug import generate_password_hash
    from getpass import getpass

    p = getpass('Enter password: ')

    GREEN = '\033[92m'
    NORMAL = '\033[0m'
    print('Your hash is {0}{1}{2}'.format(GREEN, generate_password_hash(p), NORMAL))

if __name__ == "__main__":
    manager.run()

# EOF
