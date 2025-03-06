# /backend/config.py: Contains configuration settings for the application, such as secret key, AI model, database types, encryption setup, database connection defaults, file handling, and security headers.
import os
# from cryptography.fernet import Fernet

class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY') or Fernet.generate_key().decode()
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4')
    DATABASE_TYPES = ['mongodb', 'mysql', 'sqlserver']
    
    # Encryption setup
    # CIPHER_SUITE = Fernet(Fernet.generate_key())   skipped for dev purpose
    
    
    # Database connection defaults
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    MYSQL_URI = os.environ.get('MYSQL_URI', 'mysql+pymysql://user:password@localhost:3306/')
    SQLSERVER_URI = os.environ.get('SQLSERVER_URI', 'mssql+pyodbc://user:password@localhost:1433/')
    
    # File handling
    UPLOAD_FOLDER = './uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Security headers
    CSP = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'"]
    }

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}



# Purpose and Usage
# This code defines a configuration class Config with settings for the application, such as secret key, AI model, database types, encryption setup, database connection defaults, file handling, and security headers. It also provides separate configurations for development and production environments.