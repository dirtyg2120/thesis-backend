FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt  ./

RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["uvicorn", "--host=0.0.0.0", "app.main:app"]
