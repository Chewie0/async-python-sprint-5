import os
from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    project_name: str = 'service'
    project_host: str = '127.0.0.1'
    project_port: int = 8080
    base_dir: str = BASE_DIR
    db_dsn: str = ...
    db_echo: bool = False
    secret_key: str = ...
    algoritm: str = "HS256"
    access_token_expire_minutes: int = 600
    files_folder_name: str = 'files'
    files_folder: str = os.path.join(BASE_DIR, files_folder_name)
    compression_types: list = ['zip', '7z', 'tar']
    static_url: str = ...

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
