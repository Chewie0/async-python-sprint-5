from typing import Any, Generic, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from fastapi import Request as ClientRequest
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from abc import ABC

from src.db.db import Base
from src.services.user import RepositoryUserDB
from src.services.file import RepositoryFileDB
from src.models.models import User as UserModel
from src.models.models import File as FileModel
from src.schemes.user_schemes import UserRegister


class RepositoryUser(RepositoryUserDB[UserModel, UserRegister]):
    pass

class RepositoryFile(RepositoryFileDB[UserModel]):
    pass

user_service = RepositoryUser(UserModel)
file_service = RepositoryFile(FileModel)

class Repository(ABC):

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_status(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def create_multi(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def add_click(self, *args, **kwargs):
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)
ClickModelType = TypeVar("ClickModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
MultiCreateSchemaType = TypeVar("MultiCreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryDB(Repository, Generic[
    ModelType, ClickModelType, CreateSchemaType, MultiCreateSchemaType]):

    def __init__(self, model: Type[ModelType], request: Type[ModelType]):
        self._model = model
        self._request_model = request

    async def get(self, db: AsyncSession, obj_id: Any) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.id == obj_id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def add_click(self, db: AsyncSession, *, obj_in: ModelType, request: ClientRequest) -> ClickModelType:
        db_obj = self._request_model(url_id=obj_in, client_host=request.client.host, client_port=request.client.port)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_multi(self, db: AsyncSession, *, obj_in: MultiCreateSchemaType) -> ModelType:
        objs_in_data = jsonable_encoder(obj_in)
        objects_to_db = [self._model(**obj) for obj in objs_in_data]
        db.add_all(objects_to_db)
        await db.commit()
        for obj in objects_to_db:
            await db.refresh(obj)
        return objects_to_db

    async def delete(self, db: AsyncSession, *, obj_id: Any) -> ModelType:
        db_obj = await self.get(db, obj_id)
        db_obj.deleted = True
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_status(self, db: AsyncSession, *, obj_id: Any, limit: int, offset: int,
                         full_info: Optional[bool], ) -> Union[int, list[ClickModelType]]:
        if not full_info:
            statement = select(func.count()).select_from(self._request_model).filter(
                self._request_model.url_id == obj_id)
            result = await db.execute(statement=statement)
            return result.scalar_one_or_none()
        statement = select(self._request_model).where(self._request_model.url_id == obj_id).offset(offset).limit(limit)
        result = await db.execute(statement=statement)
        return list(result.scalars().all())
