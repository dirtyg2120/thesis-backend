from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Bot Detector"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    AUTH_PREFIX: str = "/auth"
    TWEETS_NUMBER: int = 10
    TWEEPY_CACHE_TTL: int = 3600
    CONSUMER_KEY: str
    CONSUMER_SECRET: str
    FRONTEND_URL: str
    AUTH_PRIVATE_KEY: str
    TOKEN_EXPIRATION_TIME: int = 15
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "test"
    # Number of days before analysis result get cleared
    RESULT_MAX_AGE: int

    class Config:
        env_file = ".env"


settings = Settings()
