from datetime import datetime
from typing import List

from mongoengine import (
    BooleanField,
    DateTimeField,
    DictField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    IntField,
    ListField,
    StringField,
)

from .twitter import User


class ReportKey(EmbeddedDocument):
    twitter_id: str = StringField(required=True)
    scrape_date: datetime = DateTimeField(required=True)


class Report(Document):
    user = EmbeddedDocumentField(User, required=True)
    tweets = DictField(required=True)
    report_key = EmbeddedDocumentField(ReportKey, primary_key=True)
    reporters: List[str] = ListField(StringField(), required=True)
    score: float = FloatField(required=True)
    expired: bool = BooleanField(required=True)

    meta = {"collection": "report_collection"}


class ProcessedReport(Document):
    user_id: str = StringField(primary_key=True)
    user = EmbeddedDocumentField(User, required=True)
    tweet_graph = DictField(required=True)
    label: int = IntField(required=True)

    meta = {"collection": "processed_report_collection"}
