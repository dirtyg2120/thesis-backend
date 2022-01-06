# Thesis Backend

## Bot Detector

## Installation

### Method 1:

- Install all required packages

```shell
pip install -r requirements.txt
```

- Run FastAPI on localhost and check the result on [localhost:8000](localhost:8000)

```shell
python -m app.main
```

### Method 2 (with Docker):

- Build the image

```shell
sudo docker build -t thesis-backend .
```

- Run docker container and check the result on [localhost:8000](localhost:8000)

```shell
sudo docker run -p 8000:8000 thesis-backend
```

## Usage

Example user: https://twitter.com/TheRock

- API call: http://localhost:8000/api/check?url_input=https://twitter.com/TheRock

- Execute on FastAPI docs
