from datetime import datetime
from typing import List

from mongoengine import (
    DateTimeField,
    Document,
    EmbeddedDocumentListField,
    IntField,
    StringField,
)

from app.schemas import ReportResponse

from .twitter import Tweet


class Report(Document):
    twitter_id = StringField(primary_key=True)
    name: str = StringField(required=True)
    username: str = StringField(required=True)
    created_at: datetime = DateTimeField(required=True)
    followers_count: int = IntField(required=True)
    followings_count: int = IntField(required=True)
    tweets: List[Tweet] = EmbeddedDocumentListField(Tweet, default=[])
    scrape_date: datetime = DateTimeField(required=True)
    report_count: int = IntField(required=True)

    meta = {"collection": "report_collection"}

    def to_response(self) -> ReportResponse:
        response = ReportResponse(
            id=self.twitter_id,
            name=self.name,
            username=self.username,
            created_at=self.created_at,
            followers_count=self.followers_count,
            followings_count=self.followings_count,
            tweets=self.tweets,
            scrape_date=self.scrape_date,
            report_count=self.report_count,
        )
        return response
