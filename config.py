"""
Configuration management for the email service API.

Author: AI Assistant
Created: 2025-12-02
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # Database configuration
    # Render provides DATABASE_URL automatically for PostgreSQL
    # For local development, use SQLite
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Production: Use provided DATABASE_URL (PostgreSQL on Render)
        # Fix for Render's postgres:// vs postgresql:// URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
        # Use /tmp for uploads on Render (ephemeral but works for temporary storage)
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        # Local development: Use SQLite
        base_dir = Path(__file__).parent
        db_path = base_dir / 'database.db'
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        UPLOAD_FOLDER = str(base_dir / 'uploads')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database connection pool settings for stability
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Test connections before using them
        'pool_recycle': 300,    # Recycle connections after 5 minutes
        'pool_size': 5,         # Maximum number of connections
        'max_overflow': 10,     # Maximum overflow connections
        'connect_args': {
            'connect_timeout': 10,  # Connection timeout in seconds
        }
    }
    
    # Admin user (created on first run)
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'changeme123')
    
    # Email configuration
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Form Service')
    
    # Resend API (preferred for Render - 100% free, no credit card)
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
    
    # Debug: Print to see if key is loaded (will show in Render logs on startup)
    if RESEND_API_KEY:
        print(f'✅ RESEND_API_KEY loaded: {RESEND_API_KEY[:10]}...')
    else:
        print('❌ RESEND_API_KEY not found in environment variables!')

    # Resend Test Email (Recipient for warmup/test emails - REQUIRED for Resend Free Tier)
    # Must be the same email you signed up with at Resend.com
    RESEND_TEST_EMAIL = os.getenv('RESEND_TEST_EMAIL', '')
    
    # File upload settings

    # File upload settings
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB default
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,doc,docx,txt,png,jpg,jpeg,gif,zip').split(','))
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 10))
    
    # Application URL
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    @staticmethod
    def init_app(app):
        """Initialize application with config."""
        # Create upload folder if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
