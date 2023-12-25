import os
from pydantic import BaseSettings, PostgresDsn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    project_name: str = 'service'
    project_host: str = '127.0.0.1'
    project_port: int = 8080
    base_dir: str = BASE_DIR
    db_dsn: str = ...
    db_echo: bool = True
    secret_key: str = "9b73f2a1bdd7ae163444473d29a6885ffa22ab26117068f72a5a56a74d12d1fc"
    algoritm: str = "HS256"
    access_token_expire_minutes: int = 600
    files_folder: str = 'files'
    compression_types: list = ['zip', '7z', 'tar']
    static_url: str = 'http://127.0.0.1:8080/static/files'
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
