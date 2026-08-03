import os

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    TESTING = False
    DEBUG = False
    ENV_ID = 'base'

class DevelopmentConfig(BaseConfig):
    ENV_ID = 'dev'
    DEBUG = True

class StagingConfig(BaseConfig):
    ENV_ID = 'stage'
    DEBUG = True

class ProductionConfig(BaseConfig):
    ENV_ID = 'prod'
    DEBUG = False

class TestingConfig(BaseConfig):
    ENV_ID = 'test'
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
