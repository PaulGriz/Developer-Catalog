import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'impossible-to-crack'
    # SQLite Database used for local Development Only.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///developer-catalog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class StagingConfig(BaseConfig):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(BaseConfig):
    DEVELOPMENT = True
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
