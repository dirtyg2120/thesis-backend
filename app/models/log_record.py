from datetime import datetime

from mongoengine import DateTimeField, Document, StringField


class LogRecord(Document):
    level: str = StringField(required=True)
    message: str = StringField(required=True)
    created_at: datetime = DateTimeField(default=datetime.utcnow)
    created_by: str = StringField(required=True)

    meta = {"collection": "logs"}
