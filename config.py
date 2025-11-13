import os

class Config:
    """Application configuration"""
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration - supports both SQLite and PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Check if it's PostgreSQL or SQLite
        if DATABASE_URL.startswith('sqlite'):
            # For OpenShift with persistent volume
            basedir = os.path.abspath(os.path.dirname(__file__))
            db_path = DATABASE_URL.replace('sqlite:///', '')

            # Create data directory if it doesn't exist
            data_dir = os.path.dirname(db_path) if '/' in db_path else None
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)

            SQLALCHEMY_DATABASE_URI = DATABASE_URL
        else:
            # PostgreSQL for production
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # SQLite for local development
        basedir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'bookstore.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    BOOKS_PER_PAGE = 12
