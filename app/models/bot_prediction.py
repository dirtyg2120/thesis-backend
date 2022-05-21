from datetime import datetime

from mongoengine import (
    DateTimeField,
    DictField,
    Document,
    EmbeddedDocumentField,
    FloatField,
    StringField,
)

from .twitter import User


class BotPrediction(Document):
    user_id = StringField(required=True)
    user = EmbeddedDocumentField(User, required=True)
    tweets = DictField(required=True)
    score: float = FloatField(required=True)
    timestamp: datetime = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "bot_prediction_collection"}
