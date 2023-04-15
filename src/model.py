import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import sqltypes as T
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = Column(T.BigInteger().with_variant(T.Integer, "sqlite"), autoincrement=True, primary_key=True)
    name = Column(T.String(length=128), unique=True, nullable=False)
    phone = Column(T.String(length=32), unique=True, nullable=False)
    password_hash = Column(T.String(length=128), nullable=False)
    pin_hash = Column(T.String(length=128), nullable=False)
    totp_key = Column(T.String(length=128), nullable=True)

    accounts = relationship("UserAccount", back_populates="user")


class UserAccount(db.Model):
    id = Column(T.BigInteger(), autoincrement=True, primary_key=True)
    user_id = Column(T.BigInteger(), ForeignKey("user.id"))
    initial_balance = Column(T.BigInteger(), default=0, nullable=False)
    balance = Column(T.BigInteger(), default=0, nullable=False)

    user = relationship("User", back_populates="accounts")

class Transaction(db.Model):
    id = Column(T.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    from_account_id = Column(T.BigInteger(), ForeignKey("user_account.id"), nullable=True)
    to_account_id = Column(T.BigInteger(), ForeignKey("user_account.id"), nullable=True, default=None)

    # 1 = ABC Bank, 2 = Deadlock Bank
    to_bank = Column(T.String(), default=None, nullable=True)
    from_bank = Column(T.String(), default=None, nullable=True)

    to_bank_account_number = Column(T.String(128), default=None, nullable=True)
    from_bank_account_number = Column(T.String(128), default=None, nullable=True)

    from_name = Column(T.String(128), default=None, nullable=True)
    to_name = Column(T.String(128), default=None, nullable=True)

    amount = Column(T.BigInteger(), nullable=False)
    description = Column(T.String(512), nullable=False)
    status = Column(T.Enum("success", "failed", "pending", name="TransactionStatus"), nullable=False)
    transition_token_hash = Column(T.String(128), default=None, nullable=True)
    created_at = Column(T.DateTime(), nullable=False, default=datetime.now)
    trusted_app_id = Column(T.String(64), ForeignKey("trusted_app.id"), default=None, nullable=True)


class TrustedApp(db.Model):
    id = Column(T.String(64), primary_key=True)
    name = Column(T.String(128), nullable=False, unique=True)
    secret_key_hash = Column(T.String(256), nullable=False)
