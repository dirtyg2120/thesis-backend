import logging
from datetime import datetime, timedelta

from app.models import BotPrediction

_logger = logging.getLogger(__name__)


def clean_database(max_age: timedelta) -> None:
    """Clear analysis result older than max_age"""
    now = datetime.utcnow()
    try:
        count = BotPrediction.objects(timestamp__lt=now - max_age).delete()
        _logger.info(f"Clear {count} analysis results")
    except Exception as e:
        _logger.exception(e)
