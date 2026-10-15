"""
Library Management System - Configuration Settings
=================================================
Central configuration file for database credentials and Flask settings.
All database connection parameters are defined here in one place.
"""

import os

class Config:
    # Database Settings
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '12345')
    DB_NAME = os.environ.get('DB_NAME', 'library_management')

    # Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'lms-secret-key-msbte-dms-313302-k-scheme')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

    # Staff Credentials (for student project demonstration)
    STAFF_USERNAME = os.environ.get('STAFF_USERNAME', 'admin')
    STAFF_PASSWORD = os.environ.get('STAFF_PASSWORD', 'admin123')
