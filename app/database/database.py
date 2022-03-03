from typing import Optional

from pymongo import MongoClient  # type: ignore

from app.core.config import settings


class MongoDBPipeline:
    def __init__(self):
        connection = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
        )
        self.db = connection[settings.MONGO_DB]

    def add_twitter_user(self, twitter_user_data: dict):
        twitter_user_collection = self.db["twitter_user_collection"]
        try:
            twitter_user_collection.insert_one(twitter_user_data)
        except Exception as e:
            raise e

    def retrieve_twitter_user(self, username: str) -> Optional[dict]:
        twitter_user_collection = self.db["twitter_user_collection"]
        try:
            twitter_user = twitter_user_collection.find_one({"username": username})
        except Exception as e:
            raise e

        return twitter_user
