from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json

local_test = False
try:
    # Get configuration from system variables
    config_str = os.environ.get('CONFIG')
    if config_str is None:
        raise ValueError('CONFIG environment variable is not set')
    try:
        config_dict = json.loads(config_str)
    except json.JSONDecodeError as e:
        raise ValueError('Invalid JSON string: {}'.format(e))

    if not isinstance(config_dict, dict):
        raise TypeError('Expected a dictionary object for config_dict')
    if not all(key in config_dict for key in ['HOSTNAME', 'PORT', 'DATABASE', 'USERNAME', 'PASSWORD']):
        raise ValueError('Missing one or more configuration keys')

    hostname = config_dict['HOSTNAME']
    port = config_dict['PORT']
    database = config_dict['DATABASE']
    username = config_dict['USERNAME']
    password = config_dict['PASSWORD']
except:
    import secret

    hostname = secret.HOSTNAME
    port = secret.PORT
    database = secret.DATABASE
    username = secret.USERNAME
    password = secret.PASSWORD
    local_test = secret.LOCAL_TEST

# build the connection string
connection_string = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}'

# dialect://username:password@host:port/database e.g. mysql://scott:tiger@localhost/project
if not local_test:
    engine = create_engine(connection_string)
else:
    engine = create_engine('sqlite:///project.db')

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from util import models  # import all models here to ensure they are registered properly on the metadata
    Base.metadata.create_all(bind=engine)
