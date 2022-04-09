FROM python:3.9-slim

WORKDIR /backend

COPY requirements.txt  ./

RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY . .
