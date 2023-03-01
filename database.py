from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import config

hostname = config.HOSTNAME
port = config.PORT
database = config.DATABASE
username = config.USERNAME
password = config.PASSWORD

# build the connection string
connection_string = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}'

# dialect://username:password@host:port/database e.g. mysql://scott:tiger@localhost/project
engine = create_engine(connection_string)
# engine = create_engine('sqlite:///project.db')

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
