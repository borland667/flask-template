#!/usr/bin/env python
#"""Main entry-point into the 'PyPI Portal' Flask and Celery application.
#
#This is a demo Flask application used to show how I structure my large Flask
#applications.
#
#License: MIT
#Website: https://github.com/Robpol86/Flask-Large-Application-Example
#
#Command details:
#    devserver           Run the application using the Flask Development
#                        Server. Auto-reloads files when they change.
#    tornadoserver       Run the application with Facebook's Tornado web
#                        server. Forks into multiple processes to handle
#                        several requests.
#    celerydev           Starts a Celery worker with Celery Beat in the same
#                        process.
#    celerybeat          Run a Celery Beat periodic task scheduler.
#    celeryworker        Run a Celery worker process.
#    shell               Starts a Python interactive shell with the Flask
#                        application context.
#    db                  Database related commands.
#    create_all          Only create database tables if they don't exist and
#                        then exit.

#Usage:
#    manage.py devserver [-p NUM] [-l DIR] [--config_prod]
#    manage.py tornadoserver [-p NUM] [-l DIR] [--config_prod]
#    manage.py celerydev [-l DIR] [--config_prod]
#    manage.py celerybeat [-s FILE] [--pid=FILE] [-l DIR] [--config_prod]
#    manage.py celeryworker [-n NUM] [-l DIR] [--config_prod]
#    manage.py shell [--config_prod]
#    manage.py db init
#    manage.py db migrate
#    manage.py create_all [--config_prod]
#    manage.py (-h | --help)
#
#Options:
#    --config_prod               Load the production configuration instead of
#                                development.
#    -l DIR --log_dir=DIR        Log all statements to file in this directory
#                                instead of stdout.
#                                Only ERROR statements will go to stdout. stderr
#                                is not used.
#    -n NUM --name=NUM           Celery Worker name integer.
#                                [default: 1]
#    --pid=FILE                  Celery Beat PID file.
#                                [default: ./celery_beat.pid]
#    -p NUM --port=NUM           Flask will listen on this port number.
#                                [default: 5000]
#    -s FILE --schedule=FILE     Celery Beat schedule database file.
#                                [default: ./celery_beat.db]
#
#
#                                test!
#"""

from __future__ import print_function
from functools import wraps
import logging
import logging.handlers
import os
import signal
import sys

from celery.app.log import Logging
from celery.bin.celery import main as celery_main
from docopt import docopt
import flask

from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from tornado import httpserver, ioloop, web, wsgi

from restify.application import create_app, get_config
from restify.extensions import database
#from flask.ext.celery import install_commands


#OPTIONS = docopt(__doc__) if __name__ == '__main__' else dict()
OPTIONS = dict()
app = create_app(get_config('restify.config.Config'))
migrate = Migrate(app=app, db=database)
manager = Manager(app)


class CustomFormatter(logging.Formatter):
    LEVEL_MAP = {logging.FATAL: 'F', logging.ERROR: 'E', logging.WARN: 'W', logging.INFO: 'I', logging.DEBUG: 'D'}

    def format(self, record):
        record.levelletter = self.LEVEL_MAP[record.levelno]
        return super(CustomFormatter, self).format(record)


def setup_logging(name=None):
    """Setup Google-Style logging for the entire application.

    At first I hated this but I had to use it for work, and now I prefer it. Who knew?
    From: https://github.com/twitter/commons/blob/master/src/python/twitter/common/log/formatters/glog.py

    Always logs DEBUG statements somewhere.

    Positional arguments:
    name -- Append this string to the log file filename.
    """
    log_to_disk = False

    if app.config['LOG_DIR']:
        if not os.path.isdir(app.config['LOG_DIR']):
            print('ERROR: Directory {} does not exist.'.format(app.config['LOG_DIR']))
            sys.exit(1)
        if not os.access(app.config['LOG_DIR'], os.W_OK):
            print('ERROR: No permissions to write to directory {}.'.format(app.config['LOG_DIR']))
            sys.exit(1)
        log_to_disk = True

    fmt = '%(levelletter)s%(asctime)s.%(msecs).03d %(process)d %(filename)s:%(lineno)d] %(message)s'
    datefmt = '%m%d %H:%M:%S'
    formatter = CustomFormatter(fmt, datefmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR if log_to_disk else logging.DEBUG)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console_handler)

    if log_to_disk:
        file_name = os.path.join(app.config['LOG_DIR'], 'pypi_portal_{}.log'.format(name))
        file_handler = logging.handlers.TimedRotatingFileHandler(file_name, when='d', backupCount=7)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)


def log_messages(app, port, fsh_folder):
    """Log messages common to Tornado and devserver."""
    log = logging.getLogger(__name__)
    log.info('Server is running at http://0.0.0.0:{}/'.format(port))
    log.info('Flask version: {}'.format(flask.__version__))
    log.info('DEBUG: {}'.format(app.config['DEBUG']))
    log.info('FLASK_STATICS_HELPER_FOLDER: {}'.format(fsh_folder))
    log.info('STATIC_FOLDER: {}'.format(app.static_folder))


@manager.command
def celerydev():
    setup_logging('celerydev')
    app = create_app(get_config('restify.config.Config'), no_sql=True)
    Logging._setup = True  # Disable Celery from setting up logging, already done in setup_logging().
    celery_args = ['celery', 'worker', '-B', '-s', '/tmp/celery.db', '--concurrency=5']
    with app.app_context():
        return celery_main(celery_args)


@manager.command
def celerybeat():
    setup_logging('celerybeat')
    app = create_app(get_config('restify.config.Config'), no_sql=True)
    Logging._setup = True
    celery_args = ['celery', 'beat', '-C', '--pidfile', OPTIONS['--pid'], '-s', OPTIONS['--schedule']]
    with app.app_context():
        return celery_main(celery_args)


@manager.command
def celeryworker():
    setup_logging('celeryworker{}'.format(OPTIONS['--name']))
    app = create_app(get_config('restify.config.Config'), no_sql=True)
    Logging._setup = True
    celery_args = ['celery', 'worker', '-n', OPTIONS['--name'], '-C', '--autoscale=10,1', '--without-gossip']
    with app.app_context():
        return celery_main(celery_args)


#manager.add_option('--config_prod', dest=config)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server())
#manager.add_command('test', PytestCommand)

if __name__ == '__main__':
    manager.run()