from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Bot Detector"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    AUTH_PREFIX: str = "/auth"
    TWEETS_NUMBER: int
    TWEEPY_CACHE_TTL: int = 3600
    CONSUMER_KEY: str
    CONSUMER_SECRET: str
    CALLBACK_URI: str = "oob"
    FRONTEND_URL: str
    AUTH_PRIVATE_KEY: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str

    class Config:
        env_file = ".env"


settings = Settings()
