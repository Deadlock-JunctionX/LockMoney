from pydantic import BaseModel


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
