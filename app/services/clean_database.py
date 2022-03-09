from datetime import datetime, timedelta

from app.models import TwitterUser


def clean_database(max_age: timedelta) -> None:
    """Clear analysis result older than max_age"""
    now = datetime.utcnow()
    TwitterUser.objects(timestamp__lt=now - max_age).delete()
