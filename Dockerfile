FROM python:3.8-slim-buster

EXPOSE 8080

RUN apt-get update

# Install pip requirements
WORKDIR /app
COPY requirements.txt  ./
RUN python -m pip install --upgrade pip 
RUN python -m pip install -r requirements.txt

COPY . ./

ENTRYPOINT ["python", "app/main.py"]

