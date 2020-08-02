from flask_wtf import FlaskForm
from wtforms.fields import SubmitField,StringField
from wtforms import validators

class Project_search_form(FlaskForm):
  project_igf_id = \
    StringField(
      'Project igf id',
      validators=[validators.length(min=1,max=30)])
  submit = SubmitField('Search projects')
