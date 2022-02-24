# Thesis Backend

## Bot Detector

## Installation

1. **Required `Python Version` is `3.9`**
2. Create [.env](./.env) file in the root folder. That contain multiple env variables need to be configured:

    ```
    CONSUMER_KEY=<Twitter API key>
    CONSUMER_SECRET=<Twitter API secret key>
    TWEETS_NUMBER=10
    FRONTEND_URL=http://localhost:3000
    ```

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

## Testing

Run the tests with:

```shell
pytest
```

## Usage

Example user: https://twitter.com/JohnCena

- API call: http://localhost:8000/api/check?url=https://twitter.com/JohnCena

- Use doc for more information http://localhost:8000/docs

- Execute on FastAPI docs
