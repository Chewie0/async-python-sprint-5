import sys
from fastapi import APIRouter, status
from .auth import auth_router
from .ping import ping_db_router
from .files import files_router
from .register import register_router
from starlette.responses import JSONResponse

api_router = APIRouter()

@api_router.get('/')
async def root_handler():
    return JSONResponse(status_code=status.HTTP_200_OK, content={'version': 'v1'})


@api_router.get('/info')
async def info_handler():
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'api': 'v1',
        'python': sys.version_info
    })


api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(register_router, prefix="/register", tags=["register"])
api_router.include_router(ping_db_router, prefix="/ping", tags=["ping"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
