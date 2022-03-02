from pymongo import MongoClient

from app.core.config import settings
from .database_helper import profile_helper


class MongoDBPipeline:
    def __init__(self):
        connection = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
        )
        db = connection[settings.MONGO_DB]
        self.profile_collection = db[settings.MONGO_COLLECTION]

    def retrieve_profiles(self):
        profiles = []
        for profile in self.profile_collection.find():
            profiles.append(profile_helper(profile))
        return profiles

    def add_profile(self, profile_data: dict) -> dict:
        try:
            self.profile_collection.insert_one(profile_data)
        except Exception as e:
            raise e

    def retrieve_profile(self, username: str) -> dict:
        profile = self.profile_collection.find_one({"username": username})
        if profile:
            return profile_helper(profile)
