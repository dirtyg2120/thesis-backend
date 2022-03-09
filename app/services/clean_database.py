import logging
from datetime import datetime, timedelta

from app.models import TwitterUser


def clean_database(max_age: timedelta) -> None:
    """Clear analysis result older than max_age"""
    logger = logging.getLogger(__name__)
    now = datetime.utcnow()
    try:
        count = TwitterUser.objects(timestamp__lt=now - max_age).delete()
        logger.info(f"Clear {count} analysis results")
    except Exception as e:
        logger.exception(e)
