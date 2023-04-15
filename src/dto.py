from pydantic import BaseModel, Field
from datetime import datetime


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
    type: str
    bank_id: int | None = None
    bank_account_number: int | None = None
    bank_card_number: int | None = None
    priority: int | None = None

    @classmethod
    def from_db_model(cls, model) -> "AccountDto":
        return cls(
            id=model.id,
            user_id=model.user_id,
            initial_balance=model.initial_balance,
            balance=model.balance,
            type=model.type,
            bank_id=model.bank_id,
            bank_account_number=model.bank_account_number,
            bank_card_number=model.bank_card_number,
            priority=model.priority,
        )

    @classmethod
    def from_db_model_private(cls, model) -> "AccountDto":
        return cls(
            id=model.id,
            user_id=model.user_id,
            type=model.type,
        )

class AccountListDto(BaseModel):
    items: list[AccountDto]


class TransactionDto(BaseModel):
    id: str
    from_account_id: int
    to_account_id: int
    from_user_name: str | None = None
    to_user_name: str | None = None
    amount: int
    description: str
    status: str
    trusted_app_id: int | None = None
    created_at: datetime


    @classmethod
    def from_db_model(cls, model) -> "TransactionDto":
        return cls(
            id=str(model.id),
            from_account_id=model.from_account_id,
            to_account_id=model.to_account_id,
            from_user_name=model.from_user_name,
            to_user_name=model.to_user_name,
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
    from_account_id: int
    to_account_id: int
    amount: int
    description: str = Field(..., max_length=512)
    pin: str
    totp_token: str
