from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class LoginRequest(BaseModel):
    phone: str
    password: str


class LoginResponse(BaseModel):
    token: str


class UserInfoDto(BaseModel):
    id: int
    name: str
    phone: str

    @classmethod
    def from_db_model(cls, model) -> "UserInfoDto":
        return cls(
            id=model.id,
            name=model.name,
            phone=model.phone,
        )


class AccountDto(BaseModel):
    id: int
    user_id: int
    initial_balance: int | None = None
    balance: int | None = None

    @classmethod
    def from_db_model(cls, model) -> "AccountDto":
        return cls(
            id=model.id,
            user_id=model.user_id,
            initial_balance=model.initial_balance,
            balance=model.balance,
        )

    @classmethod
    def from_db_model_private(cls, model) -> "AccountDto":
        return cls(
            id=model.id,
            user_id=model.user_id,
        )

class AccountListDto(BaseModel):
    items: list[AccountDto]


class UserTransactionContext(str, Enum):
    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"


class TransactionDto(BaseModel):
    id: str
    from_account_id: int | None = None
    to_account_id: int | None = None
    from_name: str | None = None
    to_name: str | None = None
    from_bank: str | None = None
    to_bank: str | None = None
    to_bank_account_number: str | None = None
    from_bank_account_number: str | None = None
    current_user_context: str | None = None

    amount: int
    description: str
    status: str
    trusted_app_id: str | None = None
    created_at: datetime


    @classmethod
    def from_db_model(cls, model, context: UserTransactionContext | None = None) -> "TransactionDto":
        return cls(
            id=str(model.id),
            from_account_id=model.from_account_id,
            to_account_id=model.to_account_id,
            from_name=model.from_name,
            to_name=model.to_name,
            to_bank=model.to_bank,
            current_user_context=context or model.current_user_context,
            amount=model.amount,
            description=model.description,
            status=model.status,
            created_at=model.created_at,
            trusted_app_id=model.trusted_app_id,
        )

    @classmethod
    def from_db_model_plain(cls, model) -> "TransactionDto":
        return cls(
            id=str(model.id),
            from_account_id=model.from_account_id,
            to_account_id=model.to_account_id,
            amount=model.amount,
            description=model.description,
            status=model.status,
            created_at=model.created_at,
            trusted_app_id=model.trusted_app_id,
        )

class TransactionListDto(BaseModel):
    items: list[TransactionDto]


class TransactionSubmitRequest(BaseModel):
    from_account_id: int | None = None
    to_account_id: int | None = None
    to_name: str | None = None
    from_bank: str | None = None
    to_bank: str | None = None
    to_bank_account_number: str | None = None
    from_bank_account_number: str | None = None

    amount: int
    description: str = Field(..., max_length=512)
    pin: str | None = None
    totp_token: str | None = None
