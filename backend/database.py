from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# dialect://username:password@host:port/database e.g. mysql://scott:tiger@localhost/project
engine = create_engine('sqlite:///project.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models  # import all tables from models.py, do not remove this line even if it is marked as unused
    Base.metadata.create_all(bind=engine)
