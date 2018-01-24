import os


basedir = os.path.abspath(os.path.dirname(__file__))

# Code from Google Hangout Session by Udacity's Rahul Ranjan


class Config(object):

    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'quantum-proof-password'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///developer-catalog.db')


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
