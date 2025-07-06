import logging
import time
import datetime
import os
from dotenv import load_dotenv

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from argon2 import PasswordHasher

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(get_remote_address, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")
ph = PasswordHasher()

# Global variables
todelete = []
keys = {}
adminkeys = {}
userkeys = {}
keyadmins = {}
validform = []
unauthendpoint = []
betaaccess = []
startat = time.time()

# Logger setup
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.timestamp = int(time.time())
        return super().format(record)

logger = logging.getLogger('adsforafrica')
logger.setLevel(logging.DEBUG)
if os.path.isfile(f'reqmod/logging_storage/access_{datetime.date.today().strftime("%m-%d-%Y")}.log'):
    file_handler = logging.FileHandler(f'reqmod/logging_storage/access_{datetime.date.today().strftime("%m-%d-%-Y")}.log')
    file_handler.setFormatter(CustomFormatter('[%(levelname)s][%(timestamp)d]: %(message)s'))
    logger.addHandler(file_handler)
else:
    os.makedirs('reqmod/logging_storage', exist_ok=True)
    file_handler = logging.FileHandler(f'reqmod/logging_storage/access_{datetime.date.today().strftime("%m-%d-%-Y")}.log')
    file_handler.setFormatter(CustomFormatter('[%(levelname)s][%(timestamp)d]: %(message)s'))
    logger.addHandler(file_handler)


def create_app(config_name=None):
    # Set custom template and static folders to parent directory
    import os
    # Get the directory containing the app package
    app_dir = os.path.dirname(__file__)
    # Go up one level to the project root
    project_root = os.path.dirname(app_dir)
    template_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    
    from config import config
    config_obj = config[config_name]()
    app.config.from_object(config_obj)
    
    # Set database URIs manually since they're properties
    app.config['SQLALCHEMY_DATABASE_URI'] = config_obj.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_BINDS'] = {'users': config_obj.USERS_DATABASE_URI}
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    # Import models after db initialization
    from . import models
    
    # Register blueprints
    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from .ads import bp as ads_bp
    app.register_blueprint(ads_bp, url_prefix='/ads')
    
    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Before request handlers
    @app.before_request
    def filter_invalid_requests():
        from flask import request, abort
        if request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']:
            app.logger.warning(f"Invalid HTTP method: {request.method} from IP: {request.remote_addr}")
            abort(400)
        if not request.environ.get('SERVER_PROTOCOL').startswith('HTTP/1.') and not request.environ.get('SERVER_PROTOCOL').startswith('HTTP/2'):
            app.logger.warning(f"Invalid HTTP version: {request.environ.get('SERVER_PROTOCOL')} from IP: {request.remote_addr}")
            abort(400)

    @app.before_request
    def log_request_info():
        from flask import request
        global ip
        ip = request.remote_addr
    
    return app
