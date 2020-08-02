import os,logging
from flask import render_template,flash,Response,request,redirect,url_for,escape
from . import projects
import pandas as pd
from app.db import get_projects,get_total_pages,get_project_by_project_id
from app.db import get_samples_for_project_id,get_libraries_for_project_id
from .forms import Project_search_form
from flask_paginate import Pagination, get_page_parameter

@projects.route('/',methods=('GET','POST'))
def project_home():
  try:
    projects_per_page = 20
    project_igf_id = ''
    page = 1
    page = request.args.get(get_page_parameter(), type=int, default=page)
    form = Project_search_form(request.form)
    if form.validate_on_submit():
      project_igf_id = form.project_igf_id.data
      project_igf_id = project_igf_id.strip()
      project_igf_id = escape(project_igf_id)
    else:
      if request.method=='POST':
        flash('Bad request')
        redirect(url_for('projects.project_home'))
    project_list = \
      get_projects(
        search_pattern=project_igf_id,
        page=page-1,
        projects_per_page=projects_per_page)
    if len(project_list)>0:
      total_rows = \
        get_total_pages(
          collection_name='projects',
          search_pattern=project_igf_id)
    else:
      total_rows = 0
    pagination = \
      Pagination(
        page=page,
        total=total_rows,
        search=False,
        per_page=projects_per_page,
        record_name='projects',
        css_framework='bootstrap4')
    if len(project_list) > 0:
      project_list = pd.DataFrame(project_list)
      project_list['project_id'] = \
        project_list['project_id'].\
          map(lambda x: '<a href="{0}">{1}</a>'.\
            format(url_for('projects.project_info',project_id=x),x))
      project_list = \
        project_list.\
        to_html(
          index=False,
          escape=False,
          classes='table table-hover table-responsive-sm')
    else:
      project_list = 'NO RECORDS DFOUND'
    return render_template('project/project_list.html',
                           form=form,
                           project_list=project_list,
                           pagination=pagination)
  except Exception as e:
    flash('Failed request')
    print(e)
    return None

@projects.route('/project/<project_id>',methods=('GET',))
def project_info(project_id):
  try:
    project_record = \
      get_project_by_project_id(
        project_id=project_id)
    users = project_record.get('users')
    user_html = ['<ul>']
    for i in users:
      i_items = list()
      for k,v in i.items():
        if k=='user_id':
          i_items.\
            append(
              '<a href="{0}">{1}</a>'.\
                format(url_for('users.user_info',user_id=v),v))
        else:
          i_items.append('<a>{0}</a>'.format(v))
      user_html.append('<li>{0}</li>'.format(': '.join(i_items)))
    user_html.append('</ul>')
    project_record['users'] = ''.join(user_html)
    quotes_list = project_record.get('quotes_list')
    quotes_html = ['<ul>']
    quotes_html.\
      extend(['<li><a href="{0}">{1}</a>'.\
              format(url_for('quotes.quote_info',quote_id=i),i) 
                for i in quotes_list])
    quotes_html.append('<ul>')
    project_record['quotes_list'] = ''.join(quotes_html)
    project_record = \
      pd.DataFrame([project_record]).\
      fillna('').T
    project_record.columns = ['Project data']
    project_record = \
      project_record.\
      to_html(
        index=True,
        escape=False,
        classes='table table-hover table-responsive-sm')
    return render_template(
             'project/project_home.html',
             project_list=project_record)
  except Exception as e:
    flash('Failed request')
    print(e)
    return None

@projects.route('/samples/<project_id>',methods=('GET',))
def project_samples_info(project_id):
  try:
    samples_per_page=10
    samples_list = \
      get_samples_for_project_id(
        project_id=project_id,
        page=0,
        samples_per_page=samples_per_page)
    samples_list = \
      pd.DataFrame(samples_list).\
      fillna('').\
      to_html(
        index=False,
        classes='table table-hover table-responsive-sm')
    return render_template(
             'project/project_home.html',
             project_list=samples_list)
  except Exception as _:
    flash('Failed request')
    return None

@projects.route('/libraries/<project_id>',methods=('GET',))
def project_library_info(project_id):
  try:
    libraries_per_page=10
    libraries_list = \
      get_libraries_for_project_id(
        project_id=project_id,
        page=0,
        libraries_per_page=libraries_per_page)
    libraries_list = \
      pd.DataFrame(libraries_list).\
      fillna('')
    libraries_list = \
      libraries_list.\
      to_html(
        index=False,
        classes='table table-hover table-responsive-sm')
    return render_template('project/project_home.html',project_list=libraries_list)
  except Exception as _:
    flash('Failed request')
    return None