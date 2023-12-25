import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from src.core.config import settings

from src.api.v1 import base
from src.core.logger import logger

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)
app.include_router(base.api_router, prefix='/api/v1')

if __name__ == '__main__':
    logger.info(f'Start server on http://{settings.project_host}:{settings.project_port}')
    uvicorn.run(
        'main:app',
        host=settings.project_host,
        port=settings.project_port,
    )