from datetime import datetime
from typing import List

import tweepy
from mongoengine import DateTimeField, EmbeddedDocument, ListField, StringField

from app.schemas import TweetResponse


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
