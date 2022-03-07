from datetime import datetime
from typing import Optional

from mongoengine import DateTimeField, Document, IntField, StringField


class User(Document):
    twitter_id = StringField(primary_key=True)
    name: str = StringField(required=True)
    username: str = StringField(required=True)
    created_at: datetime = DateTimeField(required=True)
    followers_count: int = IntField(required=True)
    followings_count: int = IntField(required=True)
    avatar: str = StringField(required=True)
    banner: Optional[str] = StringField()

    meta = {"collection": "twitter_user_collection"}
