from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    join_date = Column(DateTime, default=datetime.utcnow)
    last_password_change_time = Column(DateTime, unique=False, nullable=True)
    last_login = Column(DateTime, unique=False, nullable=True)

    def __init__(self, email=None, username=None, password=None):
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return {'id': self.id, 'email': self.email, 'username': self.username, 'password': self.password, }
