import os
from app import create_app, db
flask_config_name = os.environ.get('FLASK_CONFIG') or 'testing'
app = create_app(config_name=flask_config_name)

if __name__=='__main__':
  app.run(debug=True)