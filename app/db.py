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

def list_planned_runs():
  '''
  '''
  try:
    pipeline = [{
      '$project': {
        '_id': 0, 
        'run_name': 1, 
        'run_id': 1, 
        'seqrun_id': 1, 
        'datestamp': 1
        }
      }, {
      '$sort': {
        'datestamp': -1
        }
      }]
    run_list = \
      db.planned_runs.\
      aggregate(pipeline)
    run_list = list(run_list)
    return run_list
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

def create_or_update_run(run_name,run_type,status='ACTIVE',seqrun_id=None,sampleshet_data=None):
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
          seqrun_id=seqrun_id,
          sampleshet_data=sampleshet_data,
          datestamp=datetime.now()
        )
      db.planned_runs.insert_one(new_run)
    else:
      response = \
        planned_runs.\
          update_one({
            'run_name':run_name
            },{
            '$set':{
              'status':status,
              'run_type':run_type,
              'seqrun_id':seqrun_id,
              'sampleshet_data':sampleshet_data,
              'datestamp':datetime.now()
          }})
  except DuplicateKeyError as _:
    return {'error':'Duplicate run_name or run_id found'}
  except Exception as _:
    return None