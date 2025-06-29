import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    
    # Database configuration
    DB_SERVER = os.getenv('DB_SERVER', 'adsforafrica-server.database.windows.net')
    DB_PORT = os.getenv('DB_PORT', '1433')
    DB_NAME = os.getenv('DB_NAME', 'ads')
    DB_USERS_NAME = os.getenv('DB_USERS_NAME', 'userstorage')
    DB_USERNAME = os.getenv('DB_USERNAME', 'adsforafrica-server-admin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password_here')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"mssql+pyodbc://{self.DB_USERNAME}:{quote_plus(self.DB_PASSWORD)}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
    
    @property
    def USERS_DATABASE_URI(self):
        return f"mssql+pyodbc://{self.DB_USERNAME}:{quote_plus(self.DB_PASSWORD)}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_USERS_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'connect_args': {
            'Encrypt': 'yes',
            'TrustServerCertificate': 'no',
            'ConnectionTimeout': 30
        }
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
