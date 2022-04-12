from datetime import datetime
from typing import List

from mongoengine import (
    DateTimeField,
    Document,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    FloatField,
)

from .twitter import Tweet, User


class BotPrediction(Document):
    user = EmbeddedDocumentField(User, required=True)
    tweets: List[Tweet] = EmbeddedDocumentListField(Tweet, default=[])
    score: float = FloatField(required=True)
    timestamp: datetime = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "bot_prediction_collection"}
