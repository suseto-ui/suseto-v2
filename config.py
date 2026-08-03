import os

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    TESTING = False
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class StagingConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False

class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True

CONFIG_MAP = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

def get_config(name=None):
    key = (name or os.getenv('FLASK_CONFIG') or 'development').lower()
    return CONFIG_MAP.get(key, DevelopmentConfig)
