import os
from flask import Flask,escape,redirect,url_for,Response
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from config import config
from bson import json_util, ObjectId
from app.db import get_quotes,get_users,get_projects,get_user_by_user_id
from app.db import get_project_by_project_id,get_quote_by_quote_id,get_quotes_for_user_id,get_total_pages
from app.db import get_projects_for_user_id,get_samples_for_project_id,get_libraries_for_project_id
from app.db import get_active_projects_with_library,list_planned_runs,create_or_update_run
from app.db import fetch_run_data_for_run_id,get_samplesheet_data_for_planned_run_id
from flask import render_template,flash,Response,request
import pandas as pd
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField,StringField,SelectField,FormField,FieldList,IntegerField
from wtforms import validators
from flask_paginate import Pagination, get_page_parameter
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(12)
bootstrap = Bootstrap()
moment = Moment()
csrfprotect = CSRFProtect()

bootstrap.init_app(app)
moment.init_app(app)
csrfprotect.init_app(app)

class Quotes_search_form(FlaskForm):
  legacy_quote_id = \
    StringField('Quotes id',validators=[validators.length(min=1,max=20)])
  submit = SubmitField('Search quotes')

class Quotes_page_form(FlaskForm):
  def __init__(self,page,max_page):
    self.page = page
    self.max_page = max_page
    pages = SelectField('Pages',choices=range(self.max_page),default=self.page)

@app.route('/quotes',methods=('GET', 'POST'))
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
    print(legacy_quote_id)
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
    
    
    return render_template('quote_home.html',form=form,
                           quotes_list=quotes_list,
                           pagination=pagination)
  except Exception as e:
    print(e)

class User_search_form(FlaskForm):
  name = \
    StringField('name',validators=[validators.length(min=1,max=20)])
  submit = SubmitField('Search users')

@app.route('/user/<user_id>',methods=['GET'])
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
      'user_info.html',
      user_list=user_record,
      quotes_list=quotes_list,
      projects_list=project_list)
  except Exception as e:
    print(e)

@app.route('/users',methods=('GET','POST'))
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
    return render_template('user_home.html',
                           form=form,
                           user_list=user_list,
                           pagination=pagination)
  except Exception as e:
    print(e)

class Project_search_form(FlaskForm):
  project_igf_id = \
    StringField('Project igf id',validators=[validators.length(min=1,max=30)])
  submit = SubmitField('Search projects')

@app.route('/projects',methods=('GET','POST'))
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
        redirect(url_for('project_home'))
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
            format(url_for('project_info',project_id=x),x))
      project_list = \
        project_list.\
        to_html(
          index=False,
          escape=False,
          classes='table table-hover table-responsive-sm')
    else:
      project_list = 'NO RECORDS DFOUND'
    return render_template('project_list.html',
                           form=form,
                           project_list=project_list,
                           pagination=pagination)
  except Exception as e:
    print(e)

@app.route('/project/<project_id>',methods=['GET'])
def project_info(project_id):
  try:
    project_record = get_project_by_project_id(project_id=project_id)
    users = project_record.get('users')
    user_html = ['<ul>']
    for i in users:
      i_items = list()
      for k,v in i.items():
        if k=='user_id':
          i_items.append('<a href="{0}">{1}</a>'.format(url_for('user_info',user_id=v),v))
        else:
          i_items.append('<a>{0}</a>'.format(v))
      user_html.append('<li>{0}</li>'.format(': '.join(i_items)))
    user_html.append('</ul>')
    project_record['users'] = ''.join(user_html)
    quotes_list = project_record.get('quotes_list')
    quotes_html = ['<ul>']
    quotes_html.\
      extend(['<li><a href="{0}">{1}</a>'.\
              format(url_for('quote_info',quote_id=i),i) 
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
    return render_template('project_home.html',project_list=project_record)
  except Exception as e:
    print(e)

@app.route('/quote/<quote_id>',methods=['GET'])
def quote_info(quote_id):
  try:
    quote_record = get_quote_by_quote_id(quote_id=quote_id)
    users = quote_record.get('users')
    user_html = ['<ul>']
    for i in users:
      i_items = list()
      for k,v in i.items():
        if k=='user_id':
          i_items.append('<a href="{0}">{1}</a>'.format(url_for('user_info',user_id=v),v))
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
    return render_template('quote_info.html',quotes_list=quote_record)
  except Exception as e:
    print(e)

@app.route('/user_quotes/<user_id>',methods=['GET'])
def user_quotes_info(user_id):
  try:
    quotes_per_page = 20
    page = 1
    page = request.args.get(get_page_parameter(), type=int, default=page)
    total_rows, quotes_list = \
      get_quotes_for_user_id(
        user_id=user_id,
        page=page-1,
        quotes_per_page=quotes_per_page)
    pagination = \
      Pagination(
        page=page,
        total=total_rows,
        search=False,
        per_page=quotes_per_page,
        record_name='quotes')
    quotes_list = \
      pd.DataFrame(quotes_list).\
        to_html(
          index=False,
          classes='table table-hover table-responsive-sm')
    return render_template('quote_info.html',quotes_list=quotes_list,pagination=pagination)
  except Exception as e:
    print(e)

@app.route('/user_projects/<user_id>',methods=['GET'])
def user_projects_info(user_id):
  try:
    projects_per_page=20
    projects_list = \
      get_projects_for_user_id(
        user_id=user_id,
        page=0,
        projects_per_page=20)
    projects_list = \
      pd.DataFrame(projects_list).\
        to_html(
          index=False,
          classes='table table-hover table-responsive-sm')
    return render_template('project_home.html',project_list=projects_list)
  except Exception as e:
    print(e)

@app.route('/samples/<project_id>',methods=['GET'])
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
    return render_template('project_home.html',project_list=samples_list)
  except Exception as e:
    print(e)

@app.route('/libraries/<project_id>',methods=['GET'])
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
    return render_template('project_home.html',project_list=libraries_list)
  except Exception as e:
    print(e)

class Run_form(FlaskForm):
  pass

class Samplesheet_line_form(FlaskForm):
  lane = SelectField(
          'Lane',
          choices=[(str(i),str(i)) for i in range(1,9)],
          validators=[])
  project_name = SelectField(
                  'Project name',
                  choices=[],
                  validators=[])
  pool_id = SelectField(
              'Pool id',
              choices=[(str(i),str(i)) for i in range(1,11)],
              validators=[])

class Samplesheet_file_form(FlaskForm):
  run_name = \
    StringField(
      'Run name',
      validators=[validators.DataRequired()])
  seqrun_id = \
    StringField(
      'Sequencing id',
      validators=[validators.DataRequired()])
  run_type = \
    SelectField(
      'Run type',
      choices=[(None,None),('MISEQ','MISEQ'),('NEXTSEQ','NEXTSEQ'),('HISEQ4000','HISEQ4000'),('NOVASEQ','NOVASEQ')],
      validators=[validators.DataRequired()])
  status = \
    SelectField(
      'Status',
      choices=[(None,None),('ACTIVE','ACTIVE'),('FAILED','FAILED'),('FINISHED','FINISHED')],
      validators=[validators.DataRequired()])
  r1_length = \
    IntegerField(
      label='R1 cycle',
      default=151,
      validators=[validators.NumberRange(min=0)])
  r2_length = \
    IntegerField(
      label='R2 cycle',
      default=151,
      validators=[validators.NumberRange(min=0)])
  assay_info = \
    StringField(
      'Assay type',
      default='UNKNOWN',
      validators=[validators.DataRequired()])
  chemistry_info = \
    StringField(
      'Chemistry',
      default='UNKNOWN',
      validators=[validators.DataRequired()])
  adapter1_seq = \
    StringField(
      'Adepter 1',
      default='AGATCGGAAGAGCACACGTCTGAACTCCAGTCA',
      validators=[validators.DataRequired()])
  adapter2_seq = \
    StringField(
      'Adepter 2',
      default='AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT',
      validators=[validators.DataRequired()])
  rows = \
    FieldList(
      FormField(
        Samplesheet_line_form),
        min_entries=1)
  add_line = SubmitField(u'Add another line')
  remove_line = SubmitField(u'Remove one line')
  save_data = SubmitField(u'Save data')
  get_csv = SubmitField(u'Get Samplesheet')


@app.route('/edit_run/<run_id>',methods=('GET','POST'))
def edit_run(run_id):
  try:
    form = Samplesheet_file_form()
    project_list = get_active_projects_with_library()
    project_list = list(project_list)
    if len(project_list) > 0:
      project_list = project_list[0].get('valid_project_list')
      project_list = [(i,i) for i in project_list]
      project_list.insert(0,('None','None'))
    else:
      project_list = list(('None','None'))
    if request.method=='GET':
      
      run = fetch_run_data_for_run_id(run_id=run_id)
      if run is not None and \
         isinstance(run,dict):
        form = Samplesheet_file_form()
        form.run_name.data = run.get('run_name')
        form.run_type.data = run.get('run_type')
        form.status.data = run.get('status')
        form.seqrun_id.data = run.get('seqrun_id')
        form.r1_length.data = run.get('r1_length')
        form.r2_length.data = run.get('r2_length')
        form.assay_info.data = run.get('assay_info')
        form.chemistry_info.data = run.get('chemistry_info')
        form.adapter1_seq.data = run.get('adapter1_seq')
        form.adapter2_seq.data = run.get('adapter2_seq')
        form.rows.pop_entry()
        for entry in run.get('samplesheet_data'):
          row = Samplesheet_line_form()
          row.lane = entry.get('lane')
          row.project_name = entry.get('project_name')
          row.pool_id = entry.get('pool_id')
          form.rows.append_entry(row)

      for row in form.rows:
        row.form.project_name.choices = project_list
      return render_template('edit_run.html',form=form,show_get_csv=True,data=None)
    if request.method=='POST':
      if form.add_line.data:
        form.rows.append_entry()
        for row in form.rows:
          row.form.project_name.choices = project_list
        return render_template('edit_run.html',form=form,show_get_csv=True,data='A')
      elif form.remove_line.data:
        if len(form.rows) > 0:
          form.rows.pop_entry()
        for row in form.rows:
          row.form.project_name.choices = project_list
        return render_template('edit_run.html',form=form,show_get_csv=True,data='R')
      elif form.get_csv.data:
        samplesheet_data = \
          get_samplesheet_data_for_planned_run_id(
            run_id=run_id)
        return Response(
                 samplesheet_data,
                 mimetype="text/csv",
                 headers={"Content-disposition":
                          "attachment; filename=SampleSheet.csv"})
      elif form.save_data.data:
        for row in form.rows:
          row.form.project_name.choices = project_list
        if form.validate_on_submit():
          samplesheet_data = list()
          for i in form.rows.data:
            row_data = dict()
            for k,v in i.items():
              if k != 'csrf_token':
                row_data.update({k:v})
            samplesheet_data.append(row_data)
          res = \
            create_or_update_run(
              run_name=form.run_name.data,
              run_type=form.run_type.data,
              status=form.status.data,
              samplesheet_data=samplesheet_data,
              seqrun_id=escape(form.seqrun_id.data),
              chemistry_info=escape(form.chemistry_info.data),
              r1_length=escape(form.r1_length.data),
              r2_length=escape(form.r2_length.data),
              assay_info=escape(form.assay_info.data),
              adapter1_seq=escape(form.adapter1_seq.data),
              adapter2_seq=escape(form.adapter2_seq.data)
            )
          return render_template('edit_run.html',form=form,show_get_csv=True,data=samplesheet_data)
        else:
          return render_template('edit_run.html',form=form,show_get_csv=True,data='N')
  except Exception as e:
    print(e)

class Create_new_run(FlaskForm):
  create_button = SubmitField(u'Create run')

@app.route('/planned_runs',methods=('GET','POST'))
def planned_runs():
  try:
    run_list = list_planned_runs()
    form = Create_new_run(request.form)
    if request.method=='POST':
      return redirect(url_for('create_run'))
    if len(run_list) > 0:
      for entry in run_list:
        run_name = entry.get('run_name')
        run_id = entry.get('run_id')
        entry.\
          update(
            {'run_name':'<a href="{0}">{1}</a>'.\
              format(url_for('edit_run',run_id=run_id),run_name)})
      run_list = pd.DataFrame(run_list)
      run_list.drop('run_id',axis=1,inplace=True)
      run_list = \
        run_list.\
        to_html(
          index=False,
          escape=False)
    else:
      run_list = 'NO RECORDS FOUND'
    return render_template('list_run.html',form=form,run_list=run_list)
  except Exception as e:
    print(e)

@app.route('/create_run',methods=('GET','POST'))
def create_run():
  try:
    form = Samplesheet_file_form()
    project_list = get_active_projects_with_library()
    project_list = list(project_list)
    if len(project_list) > 0:
      project_list = project_list[0].get('valid_project_list')
      project_list = [(i,i) for i in project_list]
      project_list.insert(0,('None','None'))
    else:
      project_list = list(('None','None'))

    if request.method=='GET':
      for row in form.rows:
        row.form.project_name.choices = project_list
      return render_template('edit_run.html',form=form,show_get_csv=False,data=None)
    if request.method=='POST':
      if form.add_line.data:
        form.rows.append_entry()
        for row in form.rows:
          row.form.project_name.choices = project_list
        return render_template('edit_run.html',form=form,data='A')
      elif form.remove_line.data:
        if len(form.rows) > 0:
          form.rows.pop_entry()
        for row in form.rows:
          row.form.project_name.choices = project_list
        return render_template('edit_run.html',form=form,show_get_csv=True,data='R')
      elif form.save_data.data:
        for row in form.rows:
          row.form.project_name.choices = project_list
        if form.validate_on_submit():
          samplesheet_data = list()
          for i in form.rows.data:
            row_data = dict()
            for k,v in i.items():
              if k != 'csrf_token':
                row_data.update({k:v})
            samplesheet_data.append(row_data)
          print(samplesheet_data)
          res = \
            create_or_update_run(
              run_name=escape(form.run_name.data),
              run_type=form.run_type.data,
              status=form.status.data,
              chemistry_info=escape(form.chemistry_info.data),
              r1_length=escape(form.r1_length.data),
              r2_length=escape(form.r2_length.data),
              assay_info=escape(form.assay_info.data),
              adapter1_seq=escape(form.adapter1_seq.data),
              adapter2_seq=escape(form.adapter2_seq.data),
              seqrun_id=escape(form.seqrun_id.data),
              samplesheet_data=samplesheet_data
            )
          return render_template('edit_run.html',form=form,show_get_csv=False,data=samplesheet_data)
        else:
          return render_template('edit_run.html',form=form,show_get_csv=False,data=form.errors)

      
  except Exception as e:
    print(e)

if __name__=='__main__':
  app.run(debug=True)