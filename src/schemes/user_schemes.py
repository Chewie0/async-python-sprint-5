from datetime import datetime as dt
from uuid import UUID
from pydantic import BaseModel, validator


class User(BaseModel):
    username: str

    class Config:
        orm_mode = True

class UserRegisterResponse(User):
    created_at: dt

class UserRegister(User):
    password: str

class UserAuth(UserRegister):
    pass

class CurrentUser(User):
    id: UUID
    created_at: dt

    @validator('created_at', pre=True)
    def datetime_to_str(cls, value):
        if isinstance(value, str):
            return dt.fromisoformat(value)

class Token(BaseModel):
    access_token: str
    class Config:
        orm_mode = True

class TokenData(BaseModel):
    username: str | None = None