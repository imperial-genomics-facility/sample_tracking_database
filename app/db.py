from flask import current_app, g
from werkzeug.local import LocalProxy
from pymongo import MongoClient
from bson.errors import InvalidId
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from pymongo.errors import DuplicateKeyError, OperationFailure

def get_db():
  '''
  '''
  try:
      db = getattr(g, "_database", None)
      DB_URI = current_app.config["DB_URI"]
      DB_NAME = current_app.config["DB_NAME"]
      if db is None:
        db = g._database = MongoClient(DB_URI)[DB_NAME]
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
          'user_id': 1
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
        'project_igf_id':1
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
        'Issued':1
      }
    }]
    quotes_list = list(db.quotes.aggregate(pipeline))
    return quotes_list
  except Exception as _:
    return None

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
    quote_record = db.quotes.find_one({'quote_id':quote_id},{'_id':0})
    return quote_record
  except (StopIteration,InvalidId) as _:
    return None
  except Exception as _:
    return {}

def get_project_by_project_id(project_id):
  '''
  '''
  try:
    project_record = db.projects.find_one({'project_id':project_id},{'_id':0})
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