from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from config import config
from bson import json_util, ObjectId

bootstrap = Bootstrap()
moment = Moment()
csrfprotect = CSRFProtect()

def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  config[config_name].init_app(app)
  bootstrap.init_app(app)
  moment.init_app(app)
  csrfprotect.init_app(app)

  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)
  from .users import users as user_blueprint
  app.register_blueprint(user_blueprint,url_prefix='/users')
  from .projects import projects as projects_blueprint
  app.register_blueprint(projects_blueprint,url_prefix='/projects')
  from .quotes import quotes as quote_blueprint
  app.register_blueprint(quote_blueprint,url_prefix='/quotes')
  from .run import runs as runs_blueprint
  app.register_blueprint(runs_blueprint,url_prefix='/runs')

  return app