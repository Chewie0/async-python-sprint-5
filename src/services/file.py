from abc import ABC
import os
from io import BytesIO
from pathlib import Path
from typing import Any, Generic, Optional, Type, TypeVar, Union, Annotated
from fastapi.encoders import jsonable_encoder
from fastapi import Depends
from fastapi import Request as ClientRequest, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import File as FileObj
from sqlalchemy import select, func
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from jose import JWTError, jwt

from src.db.db import Base, get_session
from src.core import settings
from src.schemes import file_schemes
from src.utils.tools import write_file, archive_file
from src.core.logger import logger


class Repository(ABC):
    def get_file_info_by_path(self, *args, **kwargs):
        raise NotImplementedError

    def get_file_info_by_id(self, *args, **kwargs):
        raise NotImplementedError

    def get_list_by_user_object(self, *args, **kwargs):
        raise NotImplementedError

    def create_or_put_file(self, *args, **kwargs):
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)


class RepositoryFileDB(Repository, Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def create_file(self, db: AsyncSession, user_obj: ModelType, file_obj: FileObj, file_path: str) -> Optional[
        ModelType]:
        if file_path.split('/')[-1] == file_obj.filename:
            full_path_to_file = os.path.join(settings.files_folder, file_path)
            path_to_db = os.path.normpath(file_path)
        else:
            full_path_to_file = os.path.join(settings.files_folder, file_path, file_obj.filename)
            path_to_db = os.path.join(os.path.normpath(file_path), file_obj.filename)
        path = Path(os.path.abspath(full_path_to_file))
        try:
            path.parent.absolute().mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='File with this name already exists'
            )
        await write_file(file_obj=file_obj, full_file_path=full_path_to_file)
        size = os.path.getsize(full_path_to_file)
        new_file = self._model(name=file_obj.filename, path=path_to_db, size=size, is_downloadable=True, user=user_obj)
        db.add(new_file)
        await db.commit()
        await db.refresh(new_file)
        return new_file

    async def get_list_files(self, db: AsyncSession, user_obj: ModelType) -> list[ModelType]:
        statement = select(self._model).where(self._model.user_id == user_obj.id)
        files = await db.execute(statement=statement)
        results = files.scalars().all()
        return [file_schemes.File.from_orm(file).dict() for file in results]

    async def get_file_by_path(self, db: AsyncSession, path: str) -> ModelType | None:
        if path.startswith('/'):
            logger.info(f'Get path of file {path}')
            statement = select(self._model).where(self._model.path == os.path.normpath(path[1:]))
        else:
            logger.info(f'Get id file {path}')
            statement = select(self._model).where(self._model.id == path)
        files = await db.execute(statement=statement)
        result = files.scalar_one_or_none()
        return result


    async def get_path_of_file(self, db: AsyncSession, path: str) -> str:
        result = await self.get_file_by_path(db=db, path=path)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Directory or file not found'
            )
        if not result.is_downloadable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You can not download this file.'
            )
        return result


    async def get_compression_file(self, db: AsyncSession, path: str, compression_type: str) -> Any:
        if compression_type not in settings.compression_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Compression type is not supported.'
            )

        file_obj = await self.get_file_by_path(db=db, path=path)
        if not file_obj:
            print('not file obj')
            if path.startswith('/'):
                path = path[1:]
            full_path = os.path.join(settings.files_folder, os.path.normpath(path))
            if not os.path.isdir(full_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Directory or file not found11'
                )
        else:
            if path == str(file_obj.id):
                full_path = os.path.join(settings.files_folder, file_obj.path)
            else:
                full_path = os.path.join(settings.files_folder, path)
        print(full_path)
        result, media_type, arch_name = archive_file(compression_type, full_path)
        return result, media_type, arch_name

