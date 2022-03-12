from datetime import datetime
from typing import List, Optional

from mongoengine import (
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    IntField,
    StringField,
)

from app.schemas import TweetResponse


class Tweet(EmbeddedDocument):
    tweet_id = StringField(primary_key=True)
    text: str = StringField(required=True)
    created_at: datetime = DateTimeField(required=True)

    def to_response(self) -> TweetResponse:
        response = TweetResponse(
            id=self.tweet_id, text=self.text, created_at=self.created_at
        )
        return response


class User(Document):
    twitter_id = StringField(primary_key=True)
    name: str = StringField(required=True)
    username: str = StringField(required=True)
    created_at: datetime = DateTimeField(required=True)
    followers_count: int = IntField(required=True)
    followings_count: int = IntField(required=True)
    avatar: str = StringField(required=True)
    banner: Optional[str] = StringField()
    tweets: List[Tweet] = EmbeddedDocumentListField(Tweet, default=[])
    timestamp: datetime = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "twitter_user_collection"}
