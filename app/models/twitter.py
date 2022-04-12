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

from app.schemas import TweetResponse, UserInfo


class User(EmbeddedDocument):
    twitter_id = StringField(primary_key=True)
    tweets_count: int = IntField(required=True)
    name: str = StringField(required=True)
    username: str = StringField(required=True)
    created_at: datetime = DateTimeField(required=True)
    followers_count: int = IntField(required=True)
    followings_count: int = IntField(required=True)
    favourites_count: int = IntField(required=True)
    listed_count: int = IntField(required=True)
    default_profile: bool = BooleanField(required=True)
    default_profile_image: bool = BooleanField(required=True)
    protected: bool = BooleanField(required=True)
    verified: bool = BooleanField(required=True)
    avatar: str = StringField(required=True)
    banner: Optional[str] = StringField()

    def to_user_info(self):
        response = UserInfo(
            id=self.twitter_id,
            name=self.name,
            username=self.username,
            created_at=self.created_at,
            followers_count=self.followers_count,
            followings_count=self.followings_count,
            verified=self.verified,
            avatar=self.avatar,
            banner=self.banner,
        )
        return response


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
