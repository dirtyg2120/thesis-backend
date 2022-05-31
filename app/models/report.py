from datetime import datetime
from typing import List

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)

from .twitter import TwitterInfo


class ReportKey(EmbeddedDocument):
    twitter_id: str = StringField(required=True)
    scrape_date: datetime = DateTimeField(required=True)


class Report(Document):
    report_key = EmbeddedDocumentField(ReportKey, primary_key=True)
    twitter_info = ReferenceField(TwitterInfo, required=True)
    reporters: List[str] = ListField(StringField(), required=True)
    score: float = FloatField(required=True)
    expired: bool = BooleanField(required=True)

    meta = {"collection": "report_collection"}


class ProcessedReport(Document):
    user_id: str = StringField(primary_key=True)
    twitter_info = ReferenceField(TwitterInfo, required=True)
    label: int = IntField(required=True)

    meta = {"collection": "processed_report_collection"}
