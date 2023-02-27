from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

with open('database.config', 'r') as f:
    lines = f.read().split(',\n')

host = lines[0].strip().split('=')[1].replace("'", "")
port = lines[1].strip().split('=')[1].replace("'", "")
user = lines[2].strip().split('=')[1].replace("'", "")
password = lines[3].strip().split('=')[1].replace("'", "")
database = lines[4].strip().split('=')[1].replace("'", "")
prefix = lines[5].strip().split('=')[1].replace("'", "")

# build the connection string
connection_string = f'{prefix}://{user}:{password}@{host}:{port}/{database}'

# dialect://username:password@host:port/database e.g. mysql://scott:tiger@localhost/project
engine = create_engine(connection_string)
# engine = create_engine('sqlite:///project.db')

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models  # import all tables from models.py, do not remove this line even if it is marked as unused
    Base.metadata.create_all(bind=engine)
