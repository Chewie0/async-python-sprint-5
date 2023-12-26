FROM python:3.10-slim-buster

COPY . /code

WORKDIR /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt