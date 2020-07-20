import os,logging
from flask import render_template,flash,Response,request
from . import quote
from app.db import get_quotes

@quote.route('/',methods=['GET'])
def quote_home():
  try:
      quotes_per_page = 20
      quotes_list = \
        get_quotes(
          search_pattern='',
          page=0,
          quotes_per_page=quotes_per_page)
      return render_template('quote/quote_home.html',quotes_list=quotes_list)
  except Exception as e:
    logging.warning('Error: {0}'.format(e))