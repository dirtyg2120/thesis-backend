from datetime import datetime

from mongoengine import DateTimeField, Document, StringField


class AnonymousSession(Document):
    session_id: str = StringField(primary_key=True)
    created_at: datetime = DateTimeField(default=datetime.utcnow)
