import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import sqltypes as T
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = Column(T.BigInteger(), autoincrement=True, primary_key=True)
    name = Column(T.String(length=128), unique=True, nullable=False)
    phone = Column(T.String(length=32), unique=True, nullable=False)
    password_hash = Column(T.String(length=64), nullable=False)
    pin_hash = Column(T.String(length=64), nullable=False)
    totp_key = Column(T.String(length=64), nullable=True)

    accounts = relationship("UserAccount", back_populates="user")


class UserAccount(db.Model):
    id = Column(T.BigInteger(), autoincrement=True, primary_key=True)
    user_id = Column(T.BigInteger(), ForeignKey("user.id"))
    name = Column(T.String(128), nullable=False)
    balance = Column(T.BigInteger(), default=0, nullable=False)
    type = Column(T.Enum("NATIVE", "BANK_ACCOUNT", "BANK_CARD"), nullable=False)
    bank_id = Column(T.Integer(), default=None, nullable=True)
    bank_account_number = Column(T.String(128), default=None, nullable=True)
    bank_card_number = Column(T.String(128), default=None, nullable=True)
    priority = Column(T.Integer(), default=1, nullable=False)

    user = relationship("User", back_populates="accounts")

class Transaction(db.Model):
    id = Column(T.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_account_id = Column(T.BigInteger(), ForeignKey("user_account.id"), nullable=False)
    to_account_id = Column(T.BigInteger(), ForeignKey("user_account.id"), nullable=False, default=None)
    amount = Column(T.BigInteger(), nullable=False)
    description = Column(T.String(512), nullable=False)
    status = Column(T.Enum("2fa_required", "success", "failed"), nullable=False)
    transition_token_hash = Column(T.String(128), default=None, nullable=True)
    created_at = Column(T.DateTime(), nullable=False, default=datetime.now)
