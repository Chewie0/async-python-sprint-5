import asyncio
import os
from http import HTTPStatus
from pathlib import Path
import aiofile as aiofile
import pytest
import pytest_asyncio
from httpx import AsyncClient

from .main import app
from src.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(
            app=app, base_url=f'http://{settings.project_host}:{settings.project_port}') as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def auth_client(client):
    username = "test_user"
    password = "testpass"
    await client.post('/api/v1/register/', json={"username": username, "password": password})
    response = await client.post('/api/v1/auth/',
                                 json={"username": username, "password": password})
    token = 'Bearer ' + response.json()['access_token']
    client.headers = {'Authorization': token}
    yield client


@pytest_asyncio.fixture(scope="function")
async def auth_client_with_file(auth_client):
    test_file_name = 'testfile123'
    with open(test_file_name, 'w+') as f:
        f.write('test')
    path_of_upload_file = Path(test_file_name)
    file = {'file': path_of_upload_file.open('rb')}
    await auth_client.post('/api/v1/files/upload', params={'path': '/testdir'}, files=file)
    yield auth_client


@pytest_asyncio.fixture(scope="function")
async def auth_client_with_file_to_arch(auth_client):
    test_file_name = '1file'
    with open(test_file_name, 'w+') as f:
        f.write('test')
    path_of_upload_file = Path(test_file_name)
    file = {'file': path_of_upload_file.open('rb')}
    await auth_client.post('/api/v1/files/upload', params={'path': '/archdir'}, files=file)
    yield auth_client


@pytest.mark.asyncio
async def test_register_user(client):
    username = "test_user1"
    response = await client.post('/api/v1/register/',
                                 json={"username": username, "password": "testpass"})
    assert response.status_code == HTTPStatus.CREATED
    assert response.json().get('username') == username

    response_double = await client.post('/api/v1/register/',
                                        json={"username": username, "password": "string"})

    assert response_double.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_auth_user(client):
    username = "test_user2"
    password = "testpass"
    wrong_pass = "1111"
    await client.post('/api/v1/register/', json={"username": username, "password": "testpass"})
    response = await client.post('/api/v1/auth/',
                                 json={"username": username, "password": password})
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()

    response_failed = await client.post('/api/v1/auth/',
                                        json={"username": username, "password": wrong_pass})
    assert response_failed.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_upload_file_and_get_list(auth_client):
    test_file_name = 'testfile'
    with open(test_file_name, 'w+') as f:
        f.write('test')

    path_of_upload_file = Path(test_file_name)
    file = {'file': path_of_upload_file.open('rb')}
    response = await auth_client.post('/api/v1/files/upload', params={'path': '/testdir'}, files=file)
    assert response.status_code == HTTPStatus.CREATED
    assert 'id' in response.json()
    response = await auth_client.get('/api/v1/files/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('files')) > 0


@pytest.mark.asyncio
async def test_download_file(auth_client_with_file):
    download_req = auth_client_with_file.build_request('GET', '/api/v1/files/download',
                                                       params={'path': '/testdir/testfile123'},
                                                       headers=auth_client_with_file.headers)
    response = await auth_client_with_file.send(download_req, stream=True)
    assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert response.headers['Location'] == settings.static_url + '/testdir/testfile123'


@pytest.mark.asyncio
async def test_download_file_in_archive(auth_client_with_file_to_arch):
    download_req = auth_client_with_file_to_arch.build_request('GET', '/api/v1/files/download',
                                                               params={'path': '/archdir/1file', 'compression': 'zip'},
                                                               headers=auth_client_with_file_to_arch.headers)
    response = await auth_client_with_file_to_arch.send(download_req)
    assert response.status_code == HTTPStatus.OK
    result_path = '../test.zip'
    async with aiofile.async_open(result_path, "wb+") as file:
        async for chunk in response.aiter_bytes():
            await file.write(chunk)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0
    os.remove(result_path)
