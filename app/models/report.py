import datetime
from typing import List
from mongoengine import DateTimeField, IntField, ListField
from app.models.twitter import Tweet, User


class Report(User):
    tweets: List[Tweet] = ListField
    scrape_date: datetime = DateTimeField(required=True)
    reset_date: datetime = DateTimeField(required=True)
    report_count: int = IntField(required=True)

    meta = {"collection": "report_collection"}