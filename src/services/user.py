from abc import ABC
from typing import Any, Generic, Optional, Type, TypeVar, Union, Annotated
from fastapi.encoders import jsonable_encoder
from fastapi import Depends
from fastapi import Request as ClientRequest, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from jose import JWTError, jwt

from src.db.db import Base, get_session
from src.schemes.user_schemes import TokenData
from src.core import settings
from src.utils.tools import get_password_hash, verify_password, create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='v1/authorization/token')

class Repository(ABC):
    def get_user_obj(self, *args, **kwargs):
        raise NotImplementedError

    def create_user(self, *args, **kwargs):
        raise NotImplementedError

    def make_token(self, *args, **kwargs):
        raise NotImplementedError

    def get_current_user(self, *args, **kwargs):
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class RepositoryUserDB(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def create_user(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        hash_pass = get_password_hash(obj_in_data.pop('password'))
        obj_in_data['password'] = hash_pass
        db_obj = self._model(**obj_in_data)
        print(obj_in_data)
        db.add(db_obj)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_user_obj(self, db: AsyncSession, *, obj_in: Any) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.username == obj_in.username)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def make_token(self, db: AsyncSession, *, obj_in: Any) -> Any:
        user_obj = await self.get_user_obj(db=db, obj_in=obj_in)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this username exists.'
            )
        if not verify_password(obj_in.password, user_obj.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(id_ = user_obj.username)
        return {'access_token': token, 'token_type': 'bearer'}

    async def get_current_user(self, db: AsyncSession = Depends(get_session),  token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algoritm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user_obj = await self.get_user_obj(db=db, obj_in=token_data)
        if user_obj is None:
            raise credentials_exception
        return user_obj

