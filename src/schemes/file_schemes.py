from datetime import datetime as dt
from typing import List
from uuid import UUID
from pydantic import BaseModel, validator


class FileBase(BaseModel):
    id: UUID
    name: str
    created_at: dt
    path: str
    size: int
    is_downloadable: bool

    class Config:
        orm_mode = True


class FileInDB(FileBase):

    @validator('created_at')
    def datetime_to_str(cls, value):
        if isinstance(value, str):
            return dt.fromisoformat(value)
        else:
            return value


class File(FileBase):

    @validator('created_at', pre=True)
    def datetime_to_str(cls, value):
        if isinstance(value, str):
            return dt.fromisoformat(value)
        else:
            return value


class FilesList(BaseModel):
    account_id: UUID
    files: List

    class Config:
        orm_mode = True


class ObjPath(BaseModel):
    path: str

    class Config:
        orm_mode = True
