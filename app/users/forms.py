from flask_wtf import FlaskForm
from wtforms.fields import SubmitField,StringField
from wtforms import validators

class User_search_form(FlaskForm):
  name = \
    StringField('name',validators=[validators.length(min=1,max=20)])
  submit = SubmitField('Search users')