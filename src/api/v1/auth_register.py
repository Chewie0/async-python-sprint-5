import time
from typing import Any, Annotated

from asyncpg import ConnectionDoesNotExistError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import OperationalError
from starlette.responses import JSONResponse

from src.core.logger import logger
from src.db.db import get_session
from src.schemes import user_schemes
from src.services.base import user_service


auth_router = APIRouter()


@auth_router.post("/register", response_model=user_schemes.UserRegisterResponse, status_code=status.HTTP_201_CREATED, description='Create new user.')
async def register_user(*, db: AsyncSession = Depends(get_session), user_in: user_schemes.UserRegister) -> Any:
    user_obj = await user_service.get_user_obj(db=db, obj_in=user_in)
    if user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this username exists.'
        )
    user = await user_service.create_user(db=db, obj_in=user_in)
    logger.info('Create user - %s', user.username)
    return user

@auth_router.post('/auth',response_model=user_schemes.Token, description='Get token for user.')
async def get_token(*, db: AsyncSession = Depends(get_session), obj_in: user_schemes.UserAuth):
    token = await user_service.make_token(db=db, obj_in=obj_in)
    return token

@auth_router.get('/test',response_model=user_schemes.UserAuth, description='Get token for user.')
async def read_users_me(current_user: Annotated[user_schemes.CurrentUser, Depends(user_service.get_current_user)]):

    return current_user