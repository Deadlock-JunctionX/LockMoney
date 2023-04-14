from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, sql
from sqlalchemy.sql import sqltypes as T

db = SQLAlchemy()


class User(db.Model):
    id = Column(T.BigInteger, autoincrement=True, primary_key=True)
    name = Column(T.String(length=128), unique=True, nullable=False)
    phone = Column(T.String(length=32), unique=True, nullable=False)
    password_hash = Column(T.String(length=64), nullable=True)
    
