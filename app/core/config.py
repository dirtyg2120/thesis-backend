from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Bot Detector"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    TWEETS_NUMBER: int
    CONSUMER_KEY: str
    CONSUMER_SECRET: str
    CALLBACK_URI: str = "oob"

    class Config:
        env_file = ".env"


settings = Settings()
