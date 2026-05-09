import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuração base da aplicação."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-super-secreta-mude-em-producao-2024'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'products')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # WhatsApp - Substitua pelo seu número com código do país (ex: 5585999999999)
    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER') or '5585999999999'

    # Admin padrão
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@luxscent.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'Admin@123'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "perfume_store_dev.db")}'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "perfume_store.db")}'
    # Para PostgreSQL: postgresql://user:password@host/dbname


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
