from datetime import datetime

from mongoengine import DateTimeField, Document, FloatField, StringField


class BotPrediction(Document):
    user_id = StringField(required=True)
    score: float = FloatField(required=True)
    timestamp: datetime = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "bot_prediction_collection"}
