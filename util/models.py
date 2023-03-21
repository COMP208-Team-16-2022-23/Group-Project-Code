from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    password_reminder = Column(String(500), nullable=True)
    join_date = Column(DateTime, default=datetime.utcnow)
    last_password_change_time = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, unique=False, nullable=True)

    def __init__(self, email=None, username=None, password=None, password_reminder=None):
        self.email = email
        self.username = username
        self.password = password
        self.password_reminder = password_reminder

    def __repr__(self):
        return {'id': self.id, 'email': self.email, 'username': self.username, 'password': self.password, }


class ProcessingProject(Base):
    """
    This class is used to store the information of the processing project.

    Attributes:
        id: the id of the processing project
        user_id: the id of the user who created the processing project
        original_file_path: the path of the original file
        current_file_path: the path of the current file
        modified_date: the date when the file is modified
    """

    __tablename__ = 'processing_projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    original_file_path = Column(String(500), nullable=False)
    current_file_path = Column(String(500), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow)

    def __init__(self, user_id=None, original_file_path=None, current_file_path=original_file_path):
        self.user_id = user_id
        self.original_file_path = original_file_path
        self.current_file_path = current_file_path

    def __repr__(self):
        return {'id': self.id, 'user_id': self.user_id, 'original_file_path': self.original_file_path,
                'current_file_path': self.current_file_path, 'modified_date': self.modified_date}
