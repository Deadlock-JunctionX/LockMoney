from pydantic import BaseModel
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


class AccountDto(BaseModel):
    id: int
    user_id: int
    initial_balance: int
    balance: int
    type: str
    bank_id: int | None = None
    bank_account_number: int | None = None
    bank_card_number: int | None = None
    priority: int


class AccountListDto(BaseModel):
    items: list[AccountDto]


class TransactionDto(BaseModel):
    id: str
    from_account_id: int
    to_account_id: int
    from_user_name: str
    to_user_name: str
    amount: int
    description: str
    status: str
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
        )

class TransactionListDto(BaseModel):
    items: list[TransactionDto]
