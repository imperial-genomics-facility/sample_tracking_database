from flask_wtf import FlaskForm
from wtforms.fields import SubmitField,StringField
from wtforms import validators

class Quotes_search_form(FlaskForm):
  legacy_quote_id = \
    StringField(
      'Quotes id',
      validators=[validators.length(min=1,max=20)])
  submit = SubmitField('Search quotes')
