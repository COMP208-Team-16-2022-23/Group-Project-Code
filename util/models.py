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
        return {'id': self.id, 'email': self.email, 'username': self.username, 'password': self.password}


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


class AnalysisProject(Base):
    """
    This class is used to store the information of the analysis project.

    Attributes:
        id: the id of the analysis project
        user_id: the id of the user who created the analysis project
        original_file_path: the path of the original file
        modified_date: the date when the file is modified
    """

    __tablename__ = 'analysis_projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    original_file_path = Column(String(500), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow)

    def __init__(self, user_id=None, original_file_path=None):
        self.user_id = user_id
        self.original_file_path = original_file_path

    def __repr__(self):
        return {'id': self.id, 'user_id': self.user_id, 'file_path': self.original_file_path,
                'modified_date': self.modified_date}


class AnalysisResult(Base):
    """
    This class is used to store the information of the analysis result.

    Attributes:
        id: the id of the analysis result
        project_id: the id of the analysis project
        result_file_path: the path of the result file
        modified_date: the date when the file is modified
    """

    __tablename__ = 'analysis_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False)
    result_file_path = Column(String(500), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow)

    def __init__(self, project_id=None, result_file_path=None):
        self.project_id = project_id
        self.result_file_path = result_file_path

    def __repr__(self):
        return {'id': self.id, 'project_id': self.project_id, 'file_path': self.result_file_path,
                'modified_date': self.modified_date}


class Post(Base):
    """
    This class is used to store the information of the post.

    Attributes:
        id: the id of the post
        author_id: the id of the user who created the post
        title: the title of the post
        body: the body of the post
        created: the date when the post is created
        modified: the date when the post is modified
    """

    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, nullable=False)
    title = Column(String(120), nullable=False)
    body = Column(String(500), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)

    def __init__(self, author_id=None, title=None, body=None):
        self.author_id = author_id
        self.title = title
        self.body = body

    def __repr__(self):
        return {'id': self.id, 'author_id': self.author_id, 'title': self.title, 'body': self.body,
                'created': self.created, 'modified': self.modified}


class Comment(Base):
    """
    This class is used to store the information of the comment.

    Attributes:
        id: the id of the comment
        author_id: the id of the user who created the comment
        post_id: the id of the post
        body: the body of the comment
        created: the date when the comment is created
        modified: the date when the comment is modified
    """

    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)
    body = Column(String(500), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)

    def __init__(self, author_id=None, post_id=None, body=None):
        self.author_id = author_id
        self.post_id = post_id
        self.body = body

    def __repr__(self):
        return {'id': self.id, 'author_id': self.author_id, 'post_id': self.post_id, 'body': self.body,
                'created': self.created, 'modified': self.modified}
