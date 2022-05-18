from datetime import datetime, timedelta

import pytz  # type: ignore

from app.core.config import settings
from app.models import BotPrediction
from app.services.clean_database import clean_database

MAX_AGE = timedelta(days=settings.RESULT_MAX_AGE)


def create_prediction(id, timestamp):
    prediction_db = BotPrediction(
        user_id=id,
        timestamp=timestamp,
        score=0,
    )
    prediction_db.save(validate=False)


def create_fake_prediction_collection():
    up_to_date_ts = [
        MAX_AGE - timedelta(seconds=1),
        MAX_AGE - timedelta(seconds=10000),
        MAX_AGE / 2,
        MAX_AGE / 4,
    ]
    expired_ts = [
        MAX_AGE,
        MAX_AGE + timedelta(seconds=10000),
        MAX_AGE * 2,
        MAX_AGE * 3,
    ]
    for i, ts in enumerate(up_to_date_ts + expired_ts):
        create_prediction(id=str(i), timestamp=datetime.utcnow() - ts)

    return len(up_to_date_ts), len(expired_ts)


def test_clean_database(client):
    num_new, num_old = create_fake_prediction_collection()
    assert BotPrediction.objects().count() == num_old + num_new
    clean_database(timedelta(days=settings.RESULT_MAX_AGE))

    users = BotPrediction.objects()
    assert users.count() == num_new
    for user in users:
        assert datetime.now(pytz.UTC) - user.timestamp < MAX_AGE
