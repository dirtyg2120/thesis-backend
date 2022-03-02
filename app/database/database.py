from pymongo import MongoClient

from app.core.config import settings
from .database_helper import profile_helper


class MongoDBPipeline:
    def __init__(self):
        connection = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
        )
        self.db = connection[settings.MONGO_DB]

    def retrieve_profiles(self):
        profiles = []
        for profile in self.profile_collection.find():
            profiles.append(profile_helper(profile))
        return profiles

    def add_profile(self, profile_data: dict) -> dict:
        profile_collection = self.db["profile_collection"]
        try:
            profile_collection.insert_one(profile_data)
        except Exception as e:
            raise e

    def retrieve_profile(self, username: str) -> dict:
        profile_collection = self.db[settings.MONGO_COLLECTION]
        profile = profile_collection.find_one({"username": username})
        if profile:
            return profile_helper(profile)
