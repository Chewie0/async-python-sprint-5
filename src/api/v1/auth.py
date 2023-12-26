from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from src.core.logger import logger
from src.db.db import get_session
from src.schemes import user_schemes
from src.services.base import user_service

auth_router = APIRouter()


@auth_router.post('/', response_model=user_schemes.Token, description='Get access token for user')
async def get_token(*, db: AsyncSession = Depends(get_session), obj_in: user_schemes.UserAuth):
    logger.info(f'Get token by {obj_in.username}')
    token = await user_service.make_token(db=db, obj_in=obj_in)
    return token
