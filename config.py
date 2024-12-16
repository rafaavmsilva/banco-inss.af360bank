import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/inss_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # API Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    
    # QI Tech API
    QITECH_API_BASE_URL = os.getenv("QITECH_API_BASE_URL", "https://api.qitech.com.br")
    QITECH_API_KEY = os.getenv("QITECH_API_KEY")
