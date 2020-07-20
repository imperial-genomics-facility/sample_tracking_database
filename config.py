import os,uuid

BASEDIR = os.path.dirname(__file__)

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or uuid.uuid4().hex
  FLASK_INSTANCE_PATH = os.environ.get('FLASK_INSTANCE_PATH') or BASEDIR

  @staticmethod
  def init_app(app):
    pass

class DevConfig(Config):
  MONGO_DB_URI = os.environ.get('DEV_DATABASE_URI')

class TestConfig(Config):
  WTF_CSRF_ENABLED = False
  MONGO_DB_URI = os.environ.get('TEST_DATABASE_URI')

class ProdConfig(Config):
  MONGO_DB_URI = os.environ.get('PROD_DATABASE_URI')

config = {
  'development':DevConfig,
  'testing':TestConfig,
  'production':ProdConfig
}