from typing import Any, Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Query
from fastapi.security import HTTPBearer
from starlette.responses import RedirectResponse, StreamingResponse

from src.core import settings
from src.core.logger import logger
from src.db.db import get_session
from src.schemes import user_schemes, file_schemes
from src.services.base import user_service, file_service

files_router = APIRouter()
security = HTTPBearer()


@files_router.get('/', response_model=file_schemes.FilesList, description='Get files list for user')
async def get_files_list(*, db: AsyncSession = Depends(get_session),
                         current_user: Annotated[user_schemes.CurrentUser, Depends(user_service.get_current_user)],
                         authorization: str = Depends(security)) -> Any:
    files = await file_service.get_list_files(db=db, user_obj=current_user)
    data = {'account_id': current_user.id, 'files': files}
    return data


@files_router.post('/upload', response_model=file_schemes.FileInDB, status_code=status.HTTP_201_CREATED,
                   description='Get token for user.')
async def upload_file(*, db: AsyncSession = Depends(get_session),
                      path: str = Query(description='Enter path to directory OR file'),
                      current_user: Annotated[user_schemes.CurrentUser, Depends(user_service.get_current_user)],
                      authorization: str = Depends(security), file: UploadFile = File(...)) -> Any:
    if path.startswith('/'):
        path = path[1:]
    if path.startswith('\\'):
        path = path[2:]
    file_obj = await file_service.create_file(db=db, user_obj=current_user, file_obj=file, file_path=path)
    logger.info('Upload/put file %s from %s', path, current_user.id)
    return file_obj


@files_router.get('/download', status_code=status.HTTP_200_OK, description='Download file')
async def download_file(*, db: AsyncSession = Depends(get_session),
                        current_user: Annotated[user_schemes.CurrentUser, Depends(user_service.get_current_user)],
                        authorization: str = Depends(security),
                        path: str = Query(description='Enter path like "/folder/to/file" OR file id'),
                        compression: Optional[str] = Query(default=None,
                                                           description='Optional. Compression type: zip, 7z, tar'),
                        ):
    if not path.startswith('/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Path must starts with / .'
        )
    logger.info(f'Download obj {path}')
    if compression:
        logger.info(f'Download in compression type {compression}')
        refreshed_io, media_type, arch_name = await file_service.get_compression_file(db=db, path=path,
                                                                                      compression_type=compression)
        return StreamingResponse(
            iter([refreshed_io.getvalue()]),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment;filename={arch_name}'}
        )
    else:
        file_obj = await file_service.get_path_of_file(db=db, path=path)
        return RedirectResponse(settings.static_url +'/'+ file_obj.path.replace('\\', '/'))
