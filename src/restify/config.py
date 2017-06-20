import logging

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus
from celery.schedules import crontab

import pymysql
pymysql.install_as_MySQLdb()

class HardCoded(object):
    """Constants used throughout the application.

    All hard coded settings/data that are not actual/official configuration options for Flask, Celery, or their
    extensions goes here.
    """
    ADMINS = ['me@me.test']
    DB_MODELS_IMPORTS = ('pypi',)  # Like CELERY_IMPORTS in CeleryConfig.
    ENVIRONMENT = property(lambda self: self.__class__.__name__)
    MAIL_EXCEPTION_THROTTLE = 24 * 60 * 60
    _SQLALCHEMY_DATABASE_DATABASE = 'restify'
    _SQLALCHEMY_DATABASE_HOSTNAME = 'localhost'
    _SQLALCHEMY_DATABASE_PASSWORD = ''
    _SQLALCHEMY_DATABASE_USERNAME = 'root'


class CeleryConfig(HardCoded):
    """Configurations used by Celery only."""
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERYD_TASK_SOFT_TIME_LIMIT = 20 * 60  # Raise exception if task takes too long.
    CELERYD_TASK_TIME_LIMIT = 30 * 60  # Kill worker if task takes way too long.
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_ACKS_LATE = True
    CELERY_DISABLE_RATE_LIMITS = True
    CELERY_IMPORTS = ('pypi',)
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TASK_RESULT_EXPIRES = 10 * 60  # Dispose of Celery Beat results after 10 minutes.
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TRACK_STARTED = True
    CELERYBEAT_SCHEDULE = {
        'pypy-every-day': dict(task='pypi.update_package_list', schedule=crontab(hour='0')),
    }


class Config(CeleryConfig):
    """Default Flask configuration inherited by all environments. Use this for development environments."""
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'jBerCHfD7dYjR2u7Lf2NkYvJ'
    SESSION_TYPE = 'filesystem'
    MAIL_SERVER = 'localhost'
    MAIL_DEFAULT_SENDER = 'osvaldo.demo@spark.co.nz'
    MAIL_SUPPRESS_SEND = True
    REDIS_URL = 'redis://localhost/0'
    CELERY_BROKER_URL = 'redis://localhost/0'
    CELERY_RESULT_BACKEND = 'redis://localhost/0'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = property(lambda self: 'mysql://{u}:{p}@{h}/{d}'.format(
        d=quote_plus(self._SQLALCHEMY_DATABASE_DATABASE), h=quote_plus(self._SQLALCHEMY_DATABASE_HOSTNAME),
        p=quote_plus(self._SQLALCHEMY_DATABASE_PASSWORD), u=quote_plus(self._SQLALCHEMY_DATABASE_USERNAME)
    ))

    LOG_LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }

    if DEBUG:
        CONSOLE_LOG_LEVEL = LOG_LEVELS['debug']
        FILE_LOG_LEVEL = LOG_LEVELS['debug']
    else:
        # Console logger is set to WARNING by default
        CONSOLE_LOG_LEVEL = LOG_LEVELS['warning']
        # File logger is set to INFO by default
        FILE_LOG_LEVEL = LOG_LEVELS['info']

    LOG_DIR = './'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s":[%(levelname)s]:[%(process)d-%(thread)d]:[%(name)s]:[%(funcName)s]: %(message)s'
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': FILE_LOG_LEVEL,
                'filename': LOG_DIR + 'restify.log',
                'maxBytes': 10485760,
                'backupCount': 10,
                'encoding': 'utf8',
                'formatter': 'verbose',
            },
            'file_debug': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'filename': LOG_DIR + 'restify-debug.log',
                'maxBytes': 10485760,
                'backupCount': 10,
                'encoding': 'utf8',
                'formatter': 'verbose',
            },
            'console': {
                'level': CONSOLE_LOG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '__main__':
                {
                    'propagate': "yes",
                    'level': 'DEBUG'
                },
            'werkzeug':
                {
                    'propagate': 'yes',
                    'level': 'DEBUG'
                },
            'restify':
                {
                    'propagate': "yes",
                    'level': 'DEBUG'
                },
        },

        'root': {
            'propagate': 'yes',
            'handlers': ['file', 'console', 'file_debug']
        }
    }


class Testing(Config):
    TESTING = True
    CELERY_ALWAYS_EAGER = True
    REDIS_URL = 'redis://localhost/1'
    _SQLALCHEMY_DATABASE_DATABASE = 'pypi_portal_testing'


class Production(Config):
    DEBUG = False
    # SECRET_KEY = None  # To be overwritten by a YAML file.
    ADMINS = ['osvaldo.demo@spark.co.nz']
    MAIL_SUPPRESS_SEND = False
    STATICS_MINIFY = True
