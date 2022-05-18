from datetime import datetime
from typing import List, Optional

import tweepy
from mongoengine import (
    BooleanField,
    DateTimeField,
    EmbeddedDocument,
    IntField,
    ListField,
    StringField,
)

from app.schemas import TweetResponse


class User(EmbeddedDocument):
    twitter_id = StringField(primary_key=True)
    name: str = StringField(required=True)
    screen_name: str = StringField(required=True)
    created_at: datetime = DateTimeField(required=True)
    statuses_count: int = IntField(required=True)
    followers_count: int = IntField(required=True)
    friends_count: int = IntField(required=True)
    favourites_count: int = IntField(required=True)
    listed_count: int = IntField(required=True)
    default_profile: bool = BooleanField(required=True)
    default_profile_image: bool = BooleanField(required=True)
    protected: bool = BooleanField(required=True)
    verified: bool = BooleanField(required=True)
    description: str = StringField(required=True)
    updated: datetime = DateTimeField(default=datetime.utcnow)
    avatar: str = StringField(required=True)
    banner: Optional[str] = StringField()


class Tweet(EmbeddedDocument):
    tweet_id = StringField(primary_key=True)
    text: str = StringField(required=True)
    created_at: datetime = DateTimeField(required=True)
    referenced_tweets: List[tweepy.ReferencedTweet] = ListField()

    def to_response(self) -> TweetResponse:
        response = TweetResponse(
            id=self.tweet_id, text=self.text, created_at=self.created_at
        )
        return response
