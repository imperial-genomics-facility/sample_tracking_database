import os,logging
from flask import render_template,flash,Response,request,redirect,url_for,escape
from . import quote
import pandas as pd
from app.db import get_quotes,get_quote_by_quote_id,get_total_pages
from .forms import Quotes_search_form
from app.db import get_quotes
from flask_paginate import Pagination, get_page_parameter

@quote.route('/',methods=('GET', 'POST'))
def quote_home():
  try:
    quotes_per_page = 20
    page = 1
    legacy_quote_id = ''
    form = Quotes_search_form(request.form)
    page = request.args.get(get_page_parameter(), type=int, default=page)
    if form.validate_on_submit():
      legacy_quote_id = form.legacy_quote_id.data
      legacy_quote_id = legacy_quote_id.strip()
      legacy_quote_id = escape(legacy_quote_id)
    else:
      if request.method=='POST':
        flash('Bad request')
        redirect(url_for('quote_home'))
    quotes_list = \
      get_quotes(
        search_pattern=legacy_quote_id,
        page=page-1,
        quotes_per_page=quotes_per_page)
    quotes_list = list(quotes_list)
    if len(quotes_list) > 0:
      total_rows = \
        get_total_pages(
          collection_name='quotes',
          search_pattern=legacy_quote_id)
      quotes_list = \
        pd.DataFrame(quotes_list)
      quotes_list['quote_id'] = \
        quotes_list['quote_id'].\
          map(lambda x: '<a href="{0}">{1}</a>'.\
                        format(url_for('quote_info',quote_id=x),x))
      quotes_list = \
        quotes_list.\
        to_html(
          index=False,
          escape=False,
          classes='table table-hover table-responsive-sm')
    else:
      quotes_list = 'NO RECORDS FOUND'
      total_rows = 0

    pagination = \
      Pagination(
        page=page,
        total=total_rows,
        search=False,
        per_page=quotes_per_page,
        record_name='quotes',
        css_framework='bootstrap4')
    return render_template('quote/quote_home.html',form=form,
                           quotes_list=quotes_list,
                           pagination=pagination)
  except Exception as _:
    flash('Failed request')
    return redirect(url_for('quote_home'))

@quote.route('/<quote_id>',methods=('GET'))
def quote_info(quote_id):
  try:
    quote_record = get_quote_by_quote_id(quote_id=quote_id)
    users = quote_record.get('users')
    user_html = ['<ul>']
    for i in users:
      i_items = list()
      for k,v in i.items():
        if k=='user_id':
          i_items.\
            append(
              '<a href="{0}">{1}</a>'.\
              format(url_for('user_info',user_id=v),v))
        else:
          i_items.append('<a>{0}</a>'.format(v))
      user_html.append('<li>{0}</li>'.format(': '.join(i_items)))
    user_html.append('</ul>')
    quote_record['users'] = ''.join(user_html)
    quote_record = \
      pd.DataFrame([quote_record]).\
        fillna('').T
    quote_record.columns = ['Quotes data']
    quote_record = \
      quote_record.\
      to_html(
        index=True,
        escape=False,
        classes='table table-hover table-responsive-sm')
    return render_template(
             'quote/quote_info.html',
             quotes_list=quote_record)
  except Exception as _:
    flash('Failed request')
    return redirect(url_for('quote_home'))