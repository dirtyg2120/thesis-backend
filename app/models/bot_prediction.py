from datetime import datetime

from mongoengine import (
    DateTimeField,
    DictField,
    Document,
    EmbeddedDocumentField,
    FloatField,
    ReferenceField,
    StringField,
)

from .twitter import TwitterInfo, User


class BotPrediction(Document):
    user_id = StringField(primary_key=True)
    twitter_info = ReferenceField(TwitterInfo, required=True)
    score: float = FloatField(required=True)
    timestamp: datetime = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "bot_prediction_collection"}
