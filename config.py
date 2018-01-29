import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # ...
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'impossible-to-crack'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'devshare-data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
