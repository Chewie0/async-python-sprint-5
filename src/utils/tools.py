import datetime
import os
import io
import tarfile
import zipfile
from os.path import basename
import py7zr
from datetime import datetime, timedelta
from typing import Callable
from aioshutil import copyfileobj
from fastapi import File as FileObj
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from src.core import settings
from src.core.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(id_: str):
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    jwt_data = {"sub": id_, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, settings.secret_key, algorithm=settings.algoritm)
    return encoded_jwt


async def write_file(file_obj: FileObj, full_file_path: str):
    with open(full_file_path, 'wb') as file:
        await copyfileobj(file_obj.file, file)


def add_to_arch(write_to_arch: Callable, full_path: str) -> None:
    if os.path.isfile(full_path):
        logger.info(f'Add to archive file {full_path}')
        write_to_arch(full_path, basename(full_path))
    else:
        logger.info(f'Add to archive folder {full_path}')
        for dirpath, dirnames, filenames in os.walk(full_path):
            for filename in filenames:
                filepath = os.path.join(settings.files_folder_name, dirpath.split(settings.files_folder_name)[1][1:], filename)
                write_to_arch(filepath)


def archive_file(compress_type: str, full_path: str) -> tuple[io.BytesIO, str, str]:
    app_type = None
    arch_name = f'archive_{datetime.now().timestamp()}.{compress_type}'
    arch_buffer = io.BytesIO()
    match compress_type:
        case "zip":
            with zipfile.ZipFile(arch_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_io:
                add_to_arch(write_to_arch=zip_io.write, full_path=full_path)
                zip_io.close()
            app_type = 'application/x-zip-compressed'
        case "tar":
            with tarfile.open(fileobj=arch_buffer, mode='w:gz') as tar:
                add_to_arch(write_to_arch=tar.add, full_path=full_path)
                tar.close()
            app_type = 'application/x-gtar'
        case "7z":
            with py7zr.SevenZipFile(arch_buffer, 'w') as seven_zip:
                add_to_arch(write_to_arch=seven_zip.write, full_path=full_path)
            app_type = 'application/x-7z-compressed'
    return arch_buffer, app_type, arch_name
