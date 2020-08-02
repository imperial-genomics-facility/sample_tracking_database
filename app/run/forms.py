from flask_wtf import FlaskForm
from wtforms.fields import SubmitField,StringField,SelectField
from wtforms.fields import FormField,FieldList,IntegerField
from wtforms import validators

class Samplesheet_line_form(FlaskForm):
  lane = \
    SelectField(
      'Lane',
      choices=[(str(i),str(i)) for i in range(1,9)],
      validators=[validators.DataRequired()])
  project_name = \
    SelectField(
      'Project name',
      choices=[],
      validators=[validators.DataRequired()])
  pool_id = \
    SelectField(
      'Pool id',
      choices=[(str(i),str(i)) for i in range(1,11)],
      validators=[validators.DataRequired()])

class Samplesheet_file_form(FlaskForm):
  run_name = \
    StringField(
      'Run name',
      validators=[validators.DataRequired(),
                  validators.Length(max=30)])
  seqrun_id = \
    StringField(
      'Sequencing id',
      validators=[validators.DataRequired(),
                  validators.Length(max=30)])
  run_type = \
    SelectField(
      'Run type',
      choices=[(None,None),
               ('MISEQ','MISEQ'),
               ('NEXTSEQ','NEXTSEQ'),
               ('HISEQ4000','HISEQ4000'),
               ('NOVASEQ','NOVASEQ')],
      validators=[validators.DataRequired()])
  status = \
    SelectField(
      'Status',
      choices=[(None,None),
               ('ACTIVE','ACTIVE'),
               ('FAILED','FAILED'),
               ('FINISHED','FINISHED')],
      validators=[validators.DataRequired()])
  r1_length = \
    IntegerField(
      label='R1 cycle',
      default=151,
      validators=[validators.NumberRange(min=0,max=400)])
  r2_length = \
    IntegerField(
      label='R2 cycle',
      default=151,
      validators=[validators.NumberRange(min=0,max=400)])
  assay_info = \
    StringField(
      'Assay type',
      default='UNKNOWN',
      validators=[validators.DataRequired(),
                  validators.Length(max=20)])
  chemistry_info = \
    StringField(
      'Chemistry',
      default='UNKNOWN',
      validators=[validators.DataRequired(),
                  validators.Length(max=20)])
  adapter1_seq = \
    StringField(
      'Adepter 1',
      default='AGATCGGAAGAGCACACGTCTGAACTCCAGTCA',
      validators=[validators.DataRequired(),
                  validators.Length(max=30)])
  adapter2_seq = \
    StringField(
      'Adepter 2',
      default='AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT',
      validators=[validators.DataRequired(),
                  validators.Length(max=30)])
  rows = \
    FieldList(
      FormField(
        Samplesheet_line_form),
        min_entries=1)
  add_line = SubmitField(u'Add another line')
  remove_line = SubmitField(u'Remove one line')
  save_data = SubmitField(u'Save and close')
  get_csv = SubmitField(u'Get Samplesheet')

class Create_new_run(FlaskForm):
  create_button = SubmitField(u'Create run')

class Search_planned_run(FlaskForm):
  input_field = \
    StringField(
      'Run lookup',
      validators=[validators.DataRequired(),
                  validators.length(min=1,max=20)])
  search_run = SubmitField(u'Search run')