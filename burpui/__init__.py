# -*- coding: utf8 -*-
"""
Burp-UI is a web-ui for burp backup written in python with Flask and
jQuery/Bootstrap
"""

import os
import sys
import logging

from flask import Flask
from flask.ext.login import LoginManager
from burpui.server import BUIServer as BurpUI
from burpui.routes import view
from burpui.api import api

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf-8')

__title__ = 'burp-ui'
__author__ = 'Benjamin SANS (Ziirish)'
__author_email__ = 'ziirish+burpui@ziirish.info'
__url__ = 'https://git.ziirish.me/ziirish/burp-ui'
__description__ = 'Burp-UI is a web-ui for burp backup written in python with Flask and jQuery/Bootstrap'
__license__ = 'BSD 3-clause'
__version__ = '0.1.0-dev'

# First, we setup the app
app = Flask(__name__)

app.config['CFG'] = None

app.secret_key = 'VpgOXNXAgcO81xFPyWj07ppN6kExNZeCDRShseNzFKV7ZCgmW2/eLn6xSlt7pYAVBj12zx2Vv9Kw3Q3jd1266A=='
app.jinja_env.globals.update(isinstance=isinstance, list=list)
app.jinja_env.globals.update(api=api)

# We initialize the core
bui = BurpUI(app)

# Then we load our routes
view.bui = bui
app.register_blueprint(view)

# We initialize the API
api.app = app
api.bui = bui
api.init_app(app)

# And the login_manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'view.login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(userid):
    if bui.auth != 'none':
        return bui.uhandler.user(userid)
    return None


def init(conf=None, debug=False, logfile=None, gunicorn=True):
    if debug and not gunicorn:
        app.config['DEBUG'] = debug
        app.config['TESTING'] = True

    if logfile:
        from logging import Formatter
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(logfile, maxBytes=1024 * 1024 * 100, backupCount=20)
        if debug:
            LOG_FORMAT = (
                '-' * 80 + '\n' +
                '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
                '%(message)s\n' +
                '-' * 80
            )
            file_handler.setLevel(logging.DEBUG)
        else:
            LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(Formatter(LOG_FORMAT))
        app.logger.addHandler(file_handler)

    if conf:
        if os.path.isfile(conf):
            app.config['CFG'] = conf
        else:
            raise IOError('File not found: \'{0}\''.format(conf))
    else:
        root = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..',
            '..',
            '..',
            '..',
            'share',
            'burpui',
            'etc'
        )
        conf_files = [
            '/etc/burp/burpui.cfg',
            os.path.join(root, 'burpui.cfg'),
            os.path.join(root, 'burpui.sample.cfg')
        ]
        for p in conf_files:
            app.logger.debug('Trying file \'%s\'', p)
            if os.path.isfile(p):
                app.config['CFG'] = p
                app.logger.debug('Using file \'%s\'', p)
                break

    bui.setup(app.config['CFG'])

    if gunicorn:
        app.wsgi_app = ReverseProxied(app.wsgi_app)

    return app


'''
Code from http://flask.pocoo.org/snippets/35/
'''
class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    In Apache:
     <Location /myprefix>
         ProxyPass http://192.168.0.1:5001
         ProxyPassReverse http://192.168.0.1:5001
         RequestHeader set X-Script-Name /myprefix
     </Location>

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)
