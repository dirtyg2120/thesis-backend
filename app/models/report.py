from datetime import datetime
from typing import List

from mongoengine import (
    BooleanField,
    DateTimeField,
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

from .tweet import Tweet


class ReportKey(EmbeddedDocument):
    twitter_id: str = StringField(required=True)
    scrape_date: datetime = DateTimeField(required=True)


class Report(Document):
    report_key = EmbeddedDocumentField(ReportKey, primary_key=True)
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
    tweets: List[Tweet] = EmbeddedDocumentListField(Tweet, default=[])
    reporters: List[str] = ListField(StringField(), required=True)
    score: float = FloatField(required=True)
    expired: bool = BooleanField(required=True)

    meta = {"collection": "report_collection"}

    def to_response(self) -> ReportResponse:
        response = ReportResponse(
            id=self.report_key.twitter_id,
            avatar=self.avatar,
            username=self.username,
            created_at=self.created_at,
            scrape_date=self.report_key.scrape_date,
            report_count=len(self.reporters),
            score=self.score,
        )
        return response
