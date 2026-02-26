# tells SQLAlchemy where to save the SQLite db file

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY','dev-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL','sqlite:///'+os.path.join(BASE_DIR, 'instance', 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HOST = '127.0.0.1'
    PORT = 8000
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

class DevConfig(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000

class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


