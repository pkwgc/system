from urllib.parse import quote_plus

class Config:
    # Database connection parameters
    DB_USER = 'pkwgc'
    DB_PASS = quote_plus('Wghfd@584521@fd')
    DB_HOST = 'rm-m5e0666vtv5234qi39o.mysql.rds.aliyuncs.com'
    DB_PORT = '3306'
    DB_NAME = 'kamicz'

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Connection pool settings for high concurrency
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 280  # Recycle connections before MySQL 8-hour timeout

    # Rate limiting settings
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = "memory://"

    # Security settings
    SECRET_KEY = 'dev'  # TODO: Change this in production
