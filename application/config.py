import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object) :
  SECRET_KEY = os.environ.get('SECRET_KEY') or "b'\xe5\xdb_5#y2LF4Q8z/\n\xec]\xe9>-\\x87/"
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
