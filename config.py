import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    
    # Database configuration - DigitalOcean PostgreSQL
    DB_HOST = os.getenv('DB_HOST', 'adsforafrica-do-user-16063394-0.i.db.ondigitalocean.com')
    DB_PORT = os.getenv('DB_PORT', '25060')
    DB_NAME = os.getenv('DB_NAME', 'defaultdb')
    DB_USERS_NAME = os.getenv('DB_USERS_NAME', 'defaultdb')
    DB_USERNAME = os.getenv('DB_USERNAME', 'doadmin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password_here')
    DB_SSLMODE = os.getenv('DB_SSLMODE', 'require')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql://{self.DB_USERNAME}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"
    
    @property
    def USERS_DATABASE_URI(self):
        return f"postgresql://{self.DB_USERNAME}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_USERS_NAME}?sslmode={self.DB_SSLMODE}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
