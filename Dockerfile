FROM python:3.10-slim-buster

COPY . /code

WORKDIR /code

RUN pip install --no-cache-dir -r /code/requirements.txt