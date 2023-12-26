from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.logger import logger
from src.db.db import get_session
from src.schemes import user_schemes
from src.services.base import user_service

register_router = APIRouter()


@register_router.post("/", response_model=user_schemes.UserRegisterResponse, status_code=status.HTTP_201_CREATED,
                  description='Create new user')
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


