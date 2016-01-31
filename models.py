import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


basedir = os.path.abspath(os.path.dirname(__file__))
app_db = Flask(__name__)
app_db.config['SECRET_KEY'] = 'you-will-never-guess'
app_db.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app_db.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app_db.config["JSON_SORT_KEYS"] = True
db = SQLAlchemy(app_db)

app_mdb = Flask(__name__)
app_mdb.config['SECRET_KEY'] = 'you-will-never-guess'
app_mdb.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///:memory:'
mdb = SQLAlchemy(app_mdb)

followers = db.Table('followers',
    db.Column('semantic_id', db.Integer, db.ForeignKey('semantics.id')),
    db.Column('function_id', db.Integer, db.ForeignKey('functions.id'))
)

class Function(db.Model):
    __tablename__ = 'functions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True)

    def to_json(self):
        function_in_json = {
            'function_id': self.id,
            'function_name': self.name,
        }
        return function_in_json

    @staticmethod
    def from_json(function_in_json):
        function = function_in_json.get('function')
        return Function(name=function)

    def __repr__(self):
        return '{}'.format(self.name)

class Semantic(db.Model):
    __tablename__ = 'semantics'
    id = db.Column(db.Integer, primary_key=True)
    semantic = db.Column(db.String(1024), unique=True, index=True)
    time = db.Column(db.Integer, index=True, default=datetime.utcnow())
    functions = db.relationship('Function',
        secondary = followers,
        backref = db.backref('semantics', lazy = 'dynamic'),
        lazy = 'dynamic')

    def to_json(self):
        semantic_in_json = {
            'semantic_id': self.id,
            'semantic': self.semantic,
            'add_time': self.time
        }
        return semantic_in_json

    def to_json(self):
        semantic_in_json = {
            'semantic_id': self.id,
            'semantic': self.semantic,
            'add_time': self.time
        }
        return semantic_in_json

    @staticmethod
    def from_json(semantic_in_json):
        semantic = semantic_in_json.get('semantic')
        return Semantic(semantic=semantic)

    def __repr__(self):
        return '<semantic_id {} semantic {}>'.format(self.id, self.semantic)

class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, unique=True, index=True)
    token = db.Column(db.String(128), unique=True,index=True)
    expire_time = db.Column(db.DateTime, unique=True,index=True)

    def to_json(self):
        session_in_json = {
            'token': self.token,
            'user_id': self.user_id
        }
        return session_in_json

    def __repr__(self):
        return '<User_id {} Token {}>'.format(self.user_id, self.token)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def to_json(self):
        user_in_json = {
            'username': self.username,
            'user_id': self.id,
        }
        return user_in_json

    @staticmethod
    def from_json(user_in_json):
        email = user_in_json.get('email')
        username = user_in_json.get('username')
        password = user_in_json.get('password')
        return User(email=email, username=username, password_hash=password)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} Password {} Email {}>'.format(self.username, self.password_hash, self.email)