import os
from flask import Flask,escape,redirect,url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from config import config
from bson import json_util, ObjectId
from app.db import get_quotes,get_users,get_projects,get_user_by_user_id
from app.db import get_project_by_project_id,get_quote_by_quote_id,get_quotes_for_user_id
from app.db import get_projects_for_user_id,get_samples_for_project_id,get_libraries_for_project_id
from flask import render_template,flash,Response,request
import pandas as pd
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField,StringField,SelectField
from wtforms import validators

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

@app.route('/quotes',methods=('GET', 'POST'))
def quote_home():
  try:
    quotes_per_page = 20
    page = 0
    legacy_quote_id = ''
    form = Quotes_search_form(request.form)
    if form.validate_on_submit():
      legacy_quote_id = form.legacy_quote_id.data
      legacy_quote_id = legacy_quote_id.strip()
      legacy_quote_id = escape(legacy_quote_id)
    else:
      flash('Bad request')
      redirect(url_for('quote_home'))

    quotes_list = \
      get_quotes(
        search_pattern=legacy_quote_id,
        page=page,
        quotes_per_page=quotes_per_page)
    quotes_list = \
      pd.DataFrame(quotes_list).\
      to_html(index=False)
    return render_template('quote_home.html',form=form,quotes_list=quotes_list)
  except Exception as e:
    print(e)

class User_search_form(FlaskForm):
  name = \
    StringField('name',validators=[validators.length(min=1,max=20)])
  submit = SubmitField('Search users')

@app.route('/users',methods=('GET','POST'))
def user_home():
  try:
    users_per_page = 20
    page = 0
    form = User_search_form(request.form)
    name = ''
    if form.validate_on_submit():
      name = form.name.data
      name = name.strip()
      name = escape(name)
    user_list = \
      get_users(
        name_pattern=name,
        page=page,
        users_per_page=users_per_page)
    user_list = \
      pd.DataFrame(user_list).\
      to_html(index=False)
    return render_template('user_home.html',form=form,user_list=user_list)
  except Exception as e:
    print(e)

@app.route('/user/<user_id>',methods=['GET'])
def user_info(user_id):
  try:
    user_record = get_user_by_user_id(user_id=user_id)
    user_record = \
      pd.DataFrame([user_record]).\
      to_html(index=False)
    quotes_per_page=20
    quotes_list = \
      get_quotes_for_user_id(
        user_id=user_id,
        page=0,
        quotes_per_page=quotes_per_page)
    quotes_list = \
      pd.DataFrame(quotes_list).\
      to_html(index=False)
    projects_per_page=20
    projects_list = \
      get_projects_for_user_id(
        user_id=user_id,
        page=0,
        projects_per_page=20)
    projects_list = \
      pd.DataFrame(projects_list).\
      to_html(index=False)
    return render_template(
      'user_info.html',
      user_list=user_record,
      quotes_list=quotes_list,
      projects_list=projects_list)
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
    page = 0
    form = Project_search_form(request.form)
    if form.validate_on_submit():
      project_igf_id = form.project_igf_id.data
      project_igf_id = project_igf_id.strip()
      project_igf_id = escape(project_igf_id)
    else:
      redirect(url_for('project_home'))
    project_list = \
      get_projects(
        search_pattern=project_igf_id,
        page=page,
        projects_per_page=projects_per_page)
    project_list = \
      pd.DataFrame(project_list).\
      to_html(index=False)
    return render_template('project_list.html',form=form,project_list=project_list)
  except Exception as e:
    print(e)

@app.route('/project/<project_id>',methods=['GET'])
def project_info(project_id):
  try:
    project_record = get_project_by_project_id(project_id=project_id)
    project_record = \
      pd.DataFrame([project_record]).\
      fillna('').T.\
      to_html(index=True)
    return render_template('project_home.html',project_list=project_record)
  except Exception as e:
    print(e)

@app.route('/quote/<quote_id>',methods=['GET'])
def quote_info(quote_id):
  try:
    quote_record = get_quote_by_quote_id(quote_id=quote_id)
    quote_record = \
      pd.DataFrame([quote_record]).\
      fillna('').T.\
      to_html(index=True)
    return render_template('quote_info.html',quotes_list=quote_record)
  except Exception as e:
    print(e)

@app.route('/user_quotes/<user_id>',methods=['GET'])
def user_quotes_info(user_id):
  try:
    quotes_per_page=20
    quotes_list = \
      get_quotes_for_user_id(
        user_id=user_id,
        page=0,
        quotes_per_page=quotes_per_page)
    quotes_list = \
      pd.DataFrame(quotes_list).\
        to_html(index=False)
    return render_template('quote_info.html',quotes_list=quotes_list)
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
        to_html(index=False)
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
      to_html(index=False)
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
      fillna('').\
      to_html(index=False)
    return render_template('project_home.html',project_list=libraries_list)
  except Exception as e:
    print(e)

if __name__=='__main__':
  app.run(debug=True)