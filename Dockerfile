FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt  ./

RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY app app

COPY .env ./

EXPOSE 8000

ENTRYPOINT ["uvicorn", "--host=0.0.0.0", "app.main:app"]
