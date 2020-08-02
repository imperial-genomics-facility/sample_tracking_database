import io
import pandas as pd
from flask import current_app, g
from werkzeug.local import LocalProxy
from pymongo import MongoClient
from bson.errors import InvalidId
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from pymongo.errors import DuplicateKeyError, OperationFailure
from datetime import datetime

def get_db():
  '''
  '''
  try:
      db = getattr(g, "_database", None)
      #DB_URI = current_app.config["DB_URI"]
      #DB_NAME = current_app.config["DB_NAME"]
      if db is None:
        #db = g._database = MongoClient(DB_URI)[DB_NAME]
        db = g._database = MongoClient('mongodb://root:example@192.168.99.100:27017').get_database('test')
      return db
  except Exception as _:
    raise

db = LocalProxy(get_db)

def get_users(name_pattern='',page=0,users_per_page=20):
  '''
  '''
  try:
    skip_count = page * users_per_page
    pipeline = [{
      '$match': {
        'name': {
          '$regex': name_pattern, 
            '$options': 'i'
          }
        }
      }, {
        '$sort': {
          'user_id': -1
        }
      }, {
        '$skip': skip_count
      }, {
        '$limit': users_per_page
      }, {
        '$project': {
          '_id': 0, 
          'user_id': 1, 
          'name': 1
        }
      }]
    user_list = list(db.user.aggregate(pipeline))
    return user_list
  except Exception as _:
    return None

def get_projects(search_pattern='',page=0,projects_per_page=20):
  '''
  '''
  try:
    skip_count = page * projects_per_page
    pipeline = [{
      '$match': {
        'project_igf_id': {
          '$regex': search_pattern, 
          '$options': 'i'
        }
      }
    }, {
      '$sort': {
        'Issued': -1
      }
    }, {
      '$skip': skip_count
    }, {
      '$limit': projects_per_page
    }, {
      '$project': {
        '_id': 0,
        'project_id':1,
        'project_igf_id':1,
        'status':'$Status',
        'Issued':1
      }
    }]
    projects_list = list(db.projects.aggregate(pipeline))
    return projects_list
  except Exception as _:
    return None

def get_quotes(search_pattern='',page=0,quotes_per_page=20):
  '''
  '''
  try:
    skip_count = page * quotes_per_page
    pipeline = [{
      '$match': {
        'quotes_legacy_id': {
          '$regex': search_pattern, 
          '$options': 'i'
        }
      }
    }, {
      '$sort': {
        'Issued': -1
      }
    }, {
      '$skip': skip_count
    }, {
      '$limit': quotes_per_page
    }, {
      '$project': {
        '_id': 0,
        'quote_id':1,
        'quotes_legacy_id':1,
        'status':'$Status',
        'Issued':1
      }
    }]
    quotes_list = db.quotes.aggregate(pipeline)
    return quotes_list
  except Exception as e:
    print(e)
    return None

def get_total_pages(collection_name,search_pattern=''):
  try:
    lookup_key = ''
    if collection_name == 'quotes':
      lookup_key = 'quotes_legacy_id'
    elif collection_name == 'projects':
      lookup_key = 'project_igf_id'
    elif collection_name == 'user':
      lookup_key = 'name'
    else:
      raise ValueError('Collection {0} not supported'.\
                         format(collection_name))
    pipeline = [{
      '$match': {
        lookup_key: {
          '$regex': search_pattern, 
          '$options': 'i'
          }
        }
      }, {
      '$count': 'total_rows'
      }]
    if collection_name == 'quotes':
      total_rows = db.quotes.aggregate(pipeline).next()
    elif collection_name == 'projects':
      total_rows = db.projects.aggregate(pipeline).next()
    elif collection_name == 'user':
      total_rows = db.user.aggregate(pipeline).next()
    else:
      raise ValueError('Collection {0} not supported'.\
                         format(collection_name))
    total_rows = total_rows.get('total_rows')
    return total_rows
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_user_by_user_id(user_id):
  '''
  '''
  try:
    user_record = db.user.find_one({'user_id':user_id},{'_id':0})
    return user_record
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_quote_by_quote_id(quote_id):
  '''
  '''
  try:
    pipeline = [{
      '$match': {
        'quote_id': quote_id
        }
      }, {
      '$lookup': {
        'from': 'user', 
        'let': {
          'user_list': '$user_list'
          }, 
        'pipeline': [{
          '$match': {
            '$expr': {
              '$in': ['$user_id', '$$user_list']
              }
            }
          }, {
          '$project': {
            '_id': 0, 
            'email': 0
            }
          }], 
        'as': 'users'
        }
      }, {
      '$project': {
        '_id': 0, 
        'user_list': 0
        }
      }, {
      '$limit': 1
    }]
    quote_record = db.quotes.aggregate(pipeline).next()
    return quote_record
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_project_by_project_id(project_id):
  '''
  '''
  try:
    pipeline = [{
      '$match': {
        'project_id': project_id
        }
      }, {
      '$lookup': {
        'from': 'user', 
        'let': {
          'user_list': '$user_list'
          }, 
        'pipeline': [{
          '$match': {
            '$expr': {
              '$in': ['$user_id', '$$user_list']
              }
            }
          }, {
          '$project': {
            '_id': 0, 
            'email': 0
            }
          }], 
        'as': 'users'
        }
      }, {
      '$project': {
        '_id': 0, 
        'user_list': 0
        }
      }, {
      '$limit': 1
      }]
    project_record = db.projects.aggregate(pipeline).next()
    return project_record
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_quotes_for_user_id(user_id,page=0,quotes_per_page=20):
  '''
  '''
  try:
    skip_count = page * quotes_per_page
    pipeline = [{
      '$match': {
        'user_id': user_id
        }
      }, {
      '$lookup': {
        'from': 'quotes', 
        'let': {
          'user_id': '$user_id'
        }, 
        'pipeline': [{
          '$match': {
            '$expr': {
              '$in': ['$$user_id', '$user_list']
              }
            }
          }, {
          '$project': {
            '_id': 0, 
            'quote_id': 1,
            'Status':1,
            'Issued':1
            }
          }], 
        'as': 'quotes'
        }
      }, {
        '$project': {
          '_id': 0, 
          'quotes': 1
          }
      }, {
        '$unwind': {
          'path': '$quotes'
          }
      }, {
        '$project': {
          'quote_id': '$quotes.quote_id',
          'status': '$quotes.Status',
          'issued': '$quotes.Issued'
          }
      }, {
        '$sort': {
          'issued': -1
          }
      }, {
        '$skip': skip_count
      }, {
        '$limit': quotes_per_page
      }]
    quote_ids = list(db.user.aggregate(pipeline))
    pipeline.append({'$count':'total_rows'})
    total_rows = db.user.aggregate(pipeline).next().get('total_rows')
    return quote_ids
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_projects_for_user_id(user_id,page=0,projects_per_page=20):
  '''
  '''
  try:
    skip_count = page * projects_per_page
    pipeline = [{
    '$match': {
      'user_id': user_id
      }
    }, {
    '$lookup': {
      'from': 'projects', 
      'let': {
        'user_id': '$user_id'
      }, 
      'pipeline': [{
        '$match': {
          '$expr': {
             '$in': [ '$$user_id', '$user_list' ]
          }
        }
      }, {
        '$project': {
          '_id': 0, 
          'project_id': 1,
          'project_igf_id':1,
          'Status':1,
          'Issued': 1
        }
      }], 
      'as': 'projects'
      }
    }, {
      '$project': {
        '_id': 0, 
        'projects': 1
      }
    }, {
      '$unwind': {
        'path': '$projects'
      }
    }, {
      '$project': {
        'project_id': '$projects.project_id',
        'project_igf_id': '$projects.project_igf_id',
        'status': '$projects.Status',
        'issued': '$projects.Issued'
      }
    }, {
      '$sort': {
        'issued': -1
      }
    }, {
      '$skip': skip_count
    }, {
      '$limit': projects_per_page
    }]
    quote_ids = list(db.user.aggregate(pipeline))
    return quote_ids
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_samples_for_project_id(project_id,page=0,samples_per_page=10):
  '''
  '''
  try:
    skip_count = page * samples_per_page
    pipeline = [{
      '$match': {
        'project_id': project_id
        }
      }, {
        '$skip': skip_count
      }, {
        '$limit': samples_per_page
      },{
        '$project':{
          '_id':0,
          'project_id':0,
          'index':0,
          'ID':0
        }  
      }]
    sample_records = list(db.samples.aggregate(pipeline))
    return sample_records
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_libraries_for_project_id(project_id,page=0,libraries_per_page=10):
  '''
  '''
  try:
    skip_count = page * libraries_per_page
    pipeline = [{
      '$match': {
        'project_id': project_id
        }
      }, {
      '$lookup': {
        'from': 'library', 
        'let': {
          'sample_id': '$sample_id'
          }, 
        'pipeline': [{
          '$match': {
            '$expr': {
              '$eq': [ '$sample_id', '$$sample_id' ]
              }
            }
          }, {
          '$project': {
            '_id': 0
            }
        }], 
        'as': 'libs'
        }
      }, {
      '$project': {
        '_id': 0, 
        'libs': 1
        }
      }, {
      '$unwind': {
        'path': '$libs'
        }
      }, {
      '$replaceRoot': {
        'newRoot': '$libs'
        }
      }, {
        '$skip': skip_count
      }, {
        '$limit': libraries_per_page
      }]
    library_records = list(db.samples.aggregate(pipeline))
    return library_records
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_active_projects_with_library():
  try:
    pipeline = [{
      '$match': {
        'Status': {
          '$regex': 'open', 
          '$options': 'i'
          }
        }
      }, {
      '$project': {
        '_id': 0,
        'project_id':1,
        'project_igf_id': 1
        }
      }, {
     '$lookup': {
        'from': 'library', 
        'localField': 'project_id', 
        'foreignField': 'project_id', 
        'as': 'library'
        }
      }, {
      '$project': {
        'project_igf_id': 1, 
        'lib_count': {
          '$size': '$library'
          }
        }
      }, {
      '$match': {
        'lib_count': {
          '$gt': 0
          }
        }
      }, {
      '$group': {
        '_id': None, 
        'valid_project_list': {
          '$addToSet': '$project_igf_id'
          }
        }
      }, {
      '$project': {
        '_id': 0
        }
      }]
    valid_projects_list = db.projects.aggregate(pipeline)
    return valid_projects_list
  except (StopIteration,InvalidId) as e:
    print(e)
    return None
  except Exception as _:
    return {}

def list_planned_runs(run_pattern='',page=0,runs_per_page=20):
  '''
  '''
  try:
    skip_count = page * runs_per_page
    pipeline = [{
      '$match': {
        '$or': [{
          'run_name': {
            '$regex': run_pattern, 
            '$options': 'i'
            }
          }, {
          'seqrun_id': {
            '$regex': run_pattern, 
            '$options': 'i'
            }
          },{
          'samplesheet_data':{
            '$elemMatch':{
              'project_name':{
                '$regex':run_pattern,
                '$options':'i'
                }
              }
            }
          }]
        }
      }, {
      '$skip': skip_count
      }, {
      '$limit': runs_per_page
      },{
      '$sort': {
        'datestamp': -1
        }
      },{
      '$project': {
        '_id': 0, 
        'run_name': 1,
        'run_id': 1,
        'seqrun_id': 1,
        'run_type':1,
        'status':1,
        'datestamp': 1,
        'projects':'$samplesheet_data.project_name'
        }
      }]
    run_list = \
      db.planned_runs.\
      aggregate(pipeline)
    run_list = list(run_list)
    pipeline= [{
      '$match': {
        '$or': [{
          'run_name': {
            '$regex': run_pattern, 
            '$options': 'i'
            }
          }, {
          'seqrun_id': {
            '$regex': run_pattern, 
            '$options': 'i'
            }
          },{
          'samplesheet_data':{
            '$elemMatch':{
              'project_name':{
                '$regex':run_pattern,
                '$options':'i'
                }
              }
            }
          }]
        }
      }, {
      '$count':'total_rows'}]
    total_rows = \
      list(db.planned_runs.aggregate(pipeline))
    if len(total_rows) > 0:
      total_rows = total_rows[0].get('total_rows')
    else:
      total_rows = 0
    return run_list,total_rows
  except (StopIteration,InvalidId) as e:
    print(e)
    return None
  except Exception as _:
    return {}

def fetch_run_data_for_run_id(run_id):
  try:
    run = db.planned_runs.find_one({'run_id':run_id},{'_id':0})
    return run
  except (StopIteration,InvalidId) as e:
    print(e)
    return None
  except Exception as _:
    return {}

def create_or_update_run(run_name,run_type=None,status='ACTIVE',chemistry_info=None,
                         r1_length=None,r2_length=None,assay_info=None,adapter2_seq=None,
                         seqrun_id=None,samplesheet_data=None,adapter1_seq=None):
  try:
    rec = db.planned_runs.find_one({'run_name':run_name})

    if rec is None:
      records = \
        list(db.planned_runs.aggregate([{
          "$group":{
            "_id":None,
            "max_id":{"$max":"$_id"}}
          },{
          "$project":{"_id":0}
          }]))
      if len(records) > 0 and \
         'max_id' in records[0]:
        max_id = records[0].get('max_id')
        if max_id == None:
          max_id = 0
      else:
        max_id = 0
      new_id = max_id + 1
      new_run = \
        dict(
          _id=new_id,
          run_id='IGFSR{:0>5}'.format(new_id),
          run_name=run_name,
          run_type=run_type,
          status=status,
          r1_length=r1_length,
          r2_length=r2_length,
          assay_info=assay_info,
          chemistry_info=chemistry_info,
          adapter1_seq=adapter1_seq,
          adapter2_seq=adapter2_seq,
          seqrun_id=seqrun_id,
          samplesheet_data=samplesheet_data,
          datestamp=datetime.now()
        )
      db.planned_runs.insert_one(new_run)
      return None
    else:
      response = \
        db.planned_runs.\
          update_one({
            'run_name':run_name
            },{
            '$set':{
              'status':status,
              'run_type':run_type,
              'r1_length':r1_length,
              'r2_length':r2_length,
              'assay_info':assay_info,
              'chemistry_info':chemistry_info,
              'adapter1_seq':adapter1_seq,
              'adapter2_seq':adapter2_seq,
              'seqrun_id':seqrun_id,
              'samplesheet_data':samplesheet_data,
              'datestamp':datetime.now()
          }})
      return response
  except DuplicateKeyError as _:
    return {'error':'Duplicate run_name or run_id found'}
  except Exception as _:
    return None

def fetch_library_for_project_id_and_pool_id(project_igf_id,pool_id=1):
  try:
    pool_id = str(pool_id)
    pipeline = [{
      '$match': {
        'project_igf_id': project_igf_id
        }
      }, {
      '$project': {
        '_id': 0, 
        'project_id': 1,
        'project_igf_id':1
        }
      }, {
      '$lookup': {
        'from': 'library',
        'let': {
          'project_id': '$project_id'
          }, 
        'pipeline': [{
          '$match': {
            '$expr': {
              '$and': [{
                '$eq': ['$project_id', '$$project_id']
                }, {
                '$eq': ['$Pool_No', pool_id]
                }]
              }
            }
          }], 
          'as': 'libraries'
        }
      }, {
      '$unwind': {
        'path': '$libraries'
        }
      }, {
      '$project': {
        'project_id': 1,
        'project_igf_id':1,
        'library_id': '$libraries.libs_id',
        'sample_id': '$libraries.sample_id',
        'sample_well': '$libraries.Well_Position',
        'I7_Index_ID': '$libraries.Index_1_ID',
        'index': '$libraries.Index1_Sequence',
        'I5_Index_ID': '$libraries.Index_2_ID',
        'index2': '$libraries.Index2_Sequence',
        'pool_id': '$libraries.Pool_No'
        }
      }, {
      '$lookup': {
        'from': 'samples',
        'let': {
          'sample_id': '$sample_id'
          }, 
        'pipeline': [{
          '$match': {
            '$expr': {
              '$eq': ['$sample_id', '$$sample_id']
              }
            }
          }, {
          '$project': {
            '_id': 0,
            'sample_igf_id': 1,
            'Sample Name': 1
            }
          }],
        'as': 'samples'
        }
      }, {
      '$unwind': {
        'path': '$samples'
        }
      }, {
      '$project': {
        'Sample_Project':'$project_igf_id',
        'Sample_ID': '$samples.sample_igf_id',
        'Sample_Name': '$samples.Sample Name',
        'Sample_ID':'$sample_id',
        'Sample_Well':'$sample_well',
        'Sample_Plate':None,
        'I7_Index_ID': 1,
        'index': 1,
        'I5_Index_ID': 1,
        'index2': 1,
        'Description':None 
        }
      }]
    records = db.projects.aggregate(pipeline)
    records = list(records)
    return records
  except (StopIteration,InvalidId) as e:
    print(e)
    return None
  except Exception as _:
    return {}

def get_samplesheet_data_for_planned_run_id(run_id,run_type=None,r1_length = 151,
                                            r2_length = 151,assay_info = 'UNKNOWN',
                                            chemistry_info = 'UNKNOWN',status='ACTIVE',
                                            adapter1_seq = 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCA',
                                            adapter2_seq = 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT'):
  try:
    pipeline = [{
      '$match': {
        'run_id': run_id
        }
      }, {
      '$project': {
        '_id': 0,
        'run_id':1,
        'run_type':1,
        'assay_info':1,
        'status':1,
        'chemistry_info':1,
        'r1_length':1,
        'r2_length':1,
        'adapter1_seq':1,
        'adapter2_seq':1,
        'samplesheet_data': 1
        }
      }, {
      '$unwind': {
        'path': '$samplesheet_data'
        }
      }, {
      '$project': {
        'lane': '$samplesheet_data.lane',
        'run_id':1,
        'run_type':1,
        'assay_info':1,
        'status':1,
        'chemistry_info':1,
        'r1_length':1,
        'r2_length':1,
        'adapter1_seq':1,
        'adapter2_seq':1,
        'project_name': '$samplesheet_data.project_name', 
        'pool_id': '$samplesheet_data.pool_id'
        }
      }]
    records = db.planned_runs.aggregate(pipeline)
    records = list(records)
    
    if len(records) > 0:
      run_type = records[0].get('run_type') if 'run_type' in records[0] else run_type
      status = records[0].get('status') if 'status' in records[0] else status
      r1_length = records[0].get('r1_length') if 'r1_length' in records[0] else r1_length
      r2_length = records[0].get('r2_length') if 'r2_length' in records[0] else r2_length
      assay_info = records[0].get('assay_info') if 'assay_info' in records[0] else assay_info
      chemistry_info = records[0].get('chemistry_info') if 'chemistry_info' in records[0] else chemistry_info
      adapter1_seq = records[0].get('adapter1_seq') if 'adapter1_seq' in records[0] else adapter1_seq
      adapter2_seq = records[0].get('adapter2_seq') if 'adapter2_seq' in records[0] else adapter2_seq
      
    samplesheet_data = [
      '[Header],,,,,,,,,,',
      'IEMFileVersion,4,,,,,,,,,',
      'Investigator Name,IGF,,,,,,,,,',
      'Experiment Name,{0},,,,,,,,,'.format(run_id),
      'Date,{0},,,,,,,,,'.format(datetime.now().strftime('%d-%b-%Y')),
      'Workflow,GenerateFASTQ,,,,,,,,,',
      'Application,{0} FASTQ Only,,,,,,,,,'.format(run_type),
      'Assay,{0},,,,,,,,,'.format(assay_info),
      'Description,,,,,,,,,,',
      'Chemistry,{0},,,,,,,,,'.format(chemistry_info),
      ',,,,,,,,,,',
      '[Reads],,,,,,,,,,',
      '{0},,,,,,,,,,'.format(int(r1_length)),
      '{0},,,,,,,,,,'.format(int(r2_length)),
      ',,,,,,,,,,',
      '[Settings],,,,,,,,,,',
      'Adapter,{0},,,,,,,,,'.format(adapter1_seq),
      'AdapterRead2,{0},,,,,,,,,'.format(adapter2_seq),
      ',,,,,,,,,,',
      '[Data],,,,,,,,,,'
    ]
    samplesheet_df = pd.DataFrame()
    columns = [
      'Sample_ID',
      'Sample_Name',
      'Sample_Plate',
      'Sample_Well',
      'I7_Index_ID',
      'index',
      'I5_Index_ID',
      'index2',
      'Sample_Project',
      'Description'
    ]
    if run_type in ('HISEQ4000','NOVASEQ'):
      columns.insert(0,'Lane')

    for entry in records:
      sr = \
        fetch_library_for_project_id_and_pool_id(
          project_igf_id=entry.get('project_name'),
          pool_id=entry.get('pool_id'))
      data = pd.DataFrame(sr)
      lane = entry.get('lane')
      
      if len(data.index) > 0:
        if run_type in ('HISEQ4000','NOVASEQ'):
          data['Lane'] = int(lane)
        if len(samplesheet_df.index) > 0:
          samplesheet_df = pd.concat([samplesheet_df,data])
        else:
          samplesheet_df = data.copy()
    samplesheet_data = '\n'.join(samplesheet_data)
    if len(samplesheet_df.index) > 0:
      csv_buf = io.StringIO()
      samplesheet_df[columns].\
        to_csv(csv_buf,index=False)
      data = csv_buf.getvalue()
      samplesheet_data = samplesheet_data + '\n' + data
    else:
      columns = ','.join(columns)
      samplesheet_data = samplesheet_data + '\n' + columns
    return samplesheet_data
  except Exception as _:
    return {}