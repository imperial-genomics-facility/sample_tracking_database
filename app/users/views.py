from . import users
import pandas as pd
from .forms import User_search_form
from flask import render_template,flash,Response,request,redirect,url_for,escape
from app.db import get_total_pages,get_users,get_user_by_user_id,get_quotes_for_user_id
from app.db import get_projects_for_user_id
from flask_paginate import Pagination, get_page_parameter

@users.route('/',methods=('GET','POST'))
def user_home():
  try:
    users_per_page = 20
    page = 1
    form = User_search_form(request.form)
    page = request.args.get(get_page_parameter(), type=int, default=page)
    name = ''
    if form.validate_on_submit():
      name = form.name.data
      name = name.strip()
      name = escape(name)
    else:
      if request.method=='POST':
        flash('Bad request')
        redirect(url_for('user_home'))
    user_list = \
      get_users(
        name_pattern=name,
        page=page-1,
        users_per_page=users_per_page)
    total_rows = \
      get_total_pages(
        collection_name='user',
        search_pattern=name)
    pagination = \
      Pagination(
        page=page,
        total=total_rows,
        search=False,
        per_page=users_per_page,
        record_name='users',
        css_framework='bootstrap4')
    user_list = pd.DataFrame(user_list)
    if len(user_list.index) > 0 :
      user_list['user_id'] = \
        user_list['user_id'].\
          map(lambda x: '<a href="{0}">{1}</a>'.\
                        format(url_for('user_info',user_id=x),x))
    user_list = \
      user_list.\
      to_html(
        index=False,
        escape=False,
        classes='table table-hover table-responsive-sm')
    return render_template('user/user_home.html',
                           form=form,
                           user_list=user_list,
                           pagination=pagination)
  except Exception as _:
    flash('Failed request')
    return redirect(url_for('user_home'))

@users.route('/<user_id>',methods=['GET'])
def user_info(user_id):
  try:
    user_record = get_user_by_user_id(user_id=user_id)
    user_record = \
      pd.DataFrame([user_record]).\
      to_html(
        index=False,
        classes='table table-hover table-responsive-sm')
    quotes_list = \
      get_quotes_for_user_id(
        user_id=user_id,
        page=0,
        quotes_per_page=200)
    if len(quotes_list) > 0:
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
      quotes_list = 'NO RECORD FOUND'
    project_list = \
      get_projects_for_user_id(
        user_id=user_id,
        page=0,
        projects_per_page=200)
    if len(project_list) > 0:
      project_list = \
        pd.DataFrame(project_list)
      project_list['project_id'] = \
        project_list['project_id'].\
          map(lambda x: '<a href="{0}">{1}</a>'.\
            format(url_for('project_info',project_id=x),x))
      project_list = \
        project_list.\
        to_html(
          index=False,
          escape=False,
          classes='table table-hover table-responsive-sm')
    else:
      project_list = 'NO RECORD FOUND'
    return render_template(
      'user/user_info.html',
      user_list=user_record,
      quotes_list=quotes_list,
      projects_list=project_list)
  except Exception as _:
    flash('Failed request')
    return redirect(url_for('user_home'))