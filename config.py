from urllib.parse import quote_plus
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

class Config:
    # Database Configuration
    DB_HOST = 'rm-m5e0666vtv5234qi39o.mysql.rds.aliyuncs.com'
    DB_NAME = 'kamicz'
    DB_USER = 'pkwgc'
    DB_PASS = quote_plus('Wghfd@584521@fd')
    DB_PORT = '3306'

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # High Concurrency Configuration
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 280

    # Rate Limiting Configuration
    RATELIMIT_DEFAULT = "1000/minute"
    RATELIMIT_STORAGE_URL = "memory://"

    # Security Configuration
    SECRET_KEY = 'your-secret-key-here'  # Change in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # Backup Configuration
    BACKUP_DIR = 'backups'
