import os

CONFIG = {
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key'),
    'ADMIN_USERNAME': os.getenv('ADMIN_USERNAME', 'admin'),
    'DEFAULT_ADMIN_PASSWORD': os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin'),
}
