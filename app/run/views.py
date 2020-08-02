from . import runs
import pandas as pd
import os,logging
from app.db import list_planned_runs,get_active_projects_with_library
from app.db import create_or_update_run,fetch_run_data_for_run_id
from app.db import get_samplesheet_data_for_planned_run_id
from flask import render_template,flash,Response,request,redirect,url_for,escape
from .forms import Samplesheet_file_form,Samplesheet_line_form
from .forms import Create_new_run, Search_planned_run
from flask_paginate import Pagination, get_page_parameter

@runs.route('/',methods=('GET','POST'))
def planned_runs():
  try:
    form = Create_new_run(request.form)
    form2 = Search_planned_run(request.form)
    runs_per_page = 20
    page = 1
    run_pattern = ''
    page = request.args.get(get_page_parameter(), type=int, default=page)
    if form2.validate_on_submit():
      run_pattern = form2.input_field.data
      run_pattern = run_pattern.strip()
      run_pattern = escape(run_pattern)
    else:
      if request.method=='POST' and \
         form2.search_run.data:
        flash('Bad request')
        redirect(url_for('runs.planned_runs'))
    run_list,total_rows = \
      list_planned_runs(
        run_pattern=run_pattern,
        page=page-1,
        runs_per_page=runs_per_page)
    if request.method=='POST' and \
       form.create_button.data:
      return redirect(url_for('runs.create_run'))
    if len(run_list) > 0:
      for entry in run_list:
        run_name = entry.get('run_name')
        run_id = entry.get('run_id')
        entry.\
          update(
            {'run_id':'<a href="{0}">{1}</a>'.\
              format(url_for('runs.edit_run',run_id=run_id),run_id)})
        projects = entry.get('projects')
        if len(projects) > 0:
          projects = ['<div>{0}</div>'.format(i) for i in set(projects)]
          projects = ''.join(projects)
          entry.update({'projects':projects})
      run_list = pd.DataFrame(run_list)
      run_list = \
        run_list.\
        to_html(
          index=False,
          escape=False)
    else:
      run_list = 'NO RECORDS FOUND'
    pagination = \
      Pagination(
        page=page,
        total=total_rows,
        search=False,
        per_page=runs_per_page,
        record_name='planned runs',
        css_framework='bootstrap4')
    return render_template(
             'run/list_run.html',
             form=form,
             form2=form2,
             run_list=run_list,
             pagination=pagination)
  except Exception as e:
    flash('Failed request')
    print(e)
    return None


@runs.route('/create_run',methods=('GET','POST'))
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
      return render_template(
               'run/edit_run.html',
               form=form,
               show_get_csv=False,
               data=None)
    if request.method=='POST':
      if form.add_line.data:
        form.rows.append_entry()
        for row in form.rows:
          row.form.project_name.choices = project_list
        return render_template(
                 'run/edit_run.html',
                 form=form,
                 show_get_csv=True)
      elif form.remove_line.data:
        if len(form.rows) > 0:
          form.rows.pop_entry()
        for row in form.rows:
          row.form.project_name.choices = project_list
        return render_template(
                 'run/edit_run.html',
                 form=form,
                 show_get_csv=True)
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
          flash('Success')
          return redirect(url_for('runs.planned_runs'))
        else:
          print(form.errors)
          return render_template(
                   'run/edit_run.html',
                   form=form,
                   show_get_csv=False)
  except Exception as e:
    flash('Failed request')
    print(e)
    return redirect(url_for('runs.planned_runs'))

@runs.route('/edit_run/<run_id>',methods=('GET','POST'))
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
      return render_template(
               'run/edit_run.html',
               form=form,
               show_get_csv=True)
    if request.method=='POST':
      if form.add_line.data:
        form.rows.append_entry()
        for row in form.rows:
          row.form.project_name.choices = project_list
        return render_template(
                 'run/edit_run.html',
                 form=form,
                 show_get_csv=True)
      elif form.remove_line.data:
        if len(form.rows) > 0:
          form.rows.pop_entry()
        for row in form.rows:
          row.form.project_name.choices = project_list
        return render_template(
                 'run/edit_run.html',
                 form=form,
                 show_get_csv=True)
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
          flash('Success')
          return redirect(url_for('runs.planned_runs'))
        else:
          return render_template(
                   'run/edit_run.html',
                   form=form,
                   show_get_csv=True)
  except Exception as _:
    flash('Failed request')
    return redirect(url_for('runs.planned_runs'))
