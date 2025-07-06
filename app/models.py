import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy

# Import db from the app package
from . import db

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(300))
    clickthrough_url = db.Column(db.String(300))
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    displays = db.Column(db.Integer, default=1000)
    ts = db.Column(db.Integer)
    tags = db.Column(db.String(100))
    campaignid = db.Column(db.Integer)
    iheight = db.Column(db.Integer)
    iwidth = db.Column(db.Integer)
    contact = db.Column(db.String(200))
    createdby = db.Column(db.String(50))
    authorizer = db.Column(db.String(200))
    reviewed = db.Column(db.Boolean, default=False)

class User(db.Model):
    __bind_key__ = 'users'
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    uuid = db.Column(db.String(1000), unique=True, nullable=False)
    apikey = db.Column(db.String(200), unique=True)
    isadmin = db.Column(db.Boolean, default=False)
    campaignid = db.Column(db.Integer)
    hashpwd = db.Column(db.String(200))
    strikes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.now)
    email = db.Column(db.String(255), unique=True)
    emailverified = db.Column(db.Boolean, default=False)
    roles = db.Column(db.String(20), nullable=False)

    @staticmethod
    def get(user_id):
        """Get user by ID for Flask-Login"""
        return User.query.get(int(user_id))
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Check if user is authenticated"""
        return True
    
    @property
    def is_active(self):
        """Check if user is active"""
        return True
    
    @property
    def is_anonymous(self):
        """Check if user is anonymous"""
        return False
