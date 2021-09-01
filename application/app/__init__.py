from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.utils import secure_filename
import datetime
import os

#UPLOAD_FOLDER = os.getcwd()

app = Flask(__name__, instance_path=os.path.abspath(os.path.dirname('instance')))
app.config["DEBUG"] = True
app.config['UPLOAD_PATH'] = 'app' 
app.config['ALLOWED_EXTENSIONS'] = ['jpg', 'png', 'img', 'pdf',
                                    'gif', 'doc', 'docx', 'ppt',
                                    'pptx', 'txt', 'xls', 'xlsx',
                                    '3fr', 'ari', 'arw', 'bay',
                                    'braw', 'crw', 'cr2', 'cr3',
                                    'cap', 'data', 'dcs', 'dcr', 
                                    'dng', 'drf', 'eip', 'erf',
                                    'fff', 'gpr', 'iiq', 'k25', 
                                    'kdc', 'mdc', 'mef', 'mos', 
                                    'mrw', 'nef', 'nrw', 'obm', 
                                    'orf', 'pef', 'pt', 'pxn',
                                    'r3d', 'ra', 'raw', 'rwl', 
                                    'rw2', 'rwz', 'sr2', 'srf',
                                    'srw', 'tif', 'x3f', 'webm',
                                    'mpg', 'ogg', 'mp4', 'mp3',
                                    'mov', 'avi', 'wmv', 'qt',
                                    'svd', 'ai', 'bmp', 'tif',
                                    'c', 'cpp', 'java', 'py', 
                                    'm4v', 'odt', 'rtf', 'tex', 'wpd'
                                    ]
# Maximum file upload size is 8 MB
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

# Force users to be logged in to see more than
#   the login page
login.login_view = 'login'

# Will force user to logout once the session timer
#   has passed
login.refresh_view = 'relogin'

login.needs_refresh_message = (u"Session timedout, please re-login")

# Explains how long each session is
login.needs_refresh_message_category = "Users are only allowed to be logged on for 5 minutes at a time."

from app import routes, models, errors
