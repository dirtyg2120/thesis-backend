from datetime import datetime
from typing import List

import tweepy
from mongoengine import (
    BooleanField,
    DateTimeField,
    DictField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    FloatField,
    IntField,
    ListField,
    StringField,
)

from app.schemas import ReportResponse

from .twitter import Tweet, User


class ReportKey(EmbeddedDocument):
    twitter_id: str = StringField(required=True)
    scrape_date: datetime = DateTimeField(required=True)


class Report(Document):
    report_key = EmbeddedDocumentField(ReportKey, primary_key=True)

    # NOTE: User.banner is never used in report!
    user = EmbeddedDocumentField(User, required=True)
    tweets: List[Tweet] = EmbeddedDocumentListField(Tweet, default=[])
    reporters: List[str] = ListField(StringField(), required=True)
    score: float = FloatField(required=True)
    expired: bool = BooleanField(required=True)

    meta = {"collection": "report_collection"}

    def to_response(self) -> ReportResponse:
        response = ReportResponse(
            id=self.report_key.twitter_id,
            avatar=self.user.avatar,
            username=self.user.username,
            created_at=self.user.created_at,
            scrape_date=self.report_key.scrape_date,
            report_count=len(self.reporters),
            score=self.score,
        )
        return response


class ProcessedReport(Document):
    twitter_id = StringField(primary_key=True)
    user: tweepy.User = DictField(required=True)
    label: int = IntField(required=True)

    meta = {"collection": "processed_report_collection"}
