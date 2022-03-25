from datetime import datetime, timedelta

import pytz  # type: ignore

from app.core.config import settings
from app.models import TwitterUser
from app.schemas import tweet
from app.services.clean_database import clean_database

MAX_AGE = timedelta(days=settings.RESULT_MAX_AGE)


def create_twitter_user(id, timestamp):
    user_db = TwitterUser(
        twitter_id=id,
        tweets_count=0,
        name="user.name",
        username="user.screen_name",
        created_at=timestamp,
        timestamp=timestamp,
        followers_count=0,
        followings_count=0,
        favourites_count=0,
        listed_count=0,
        default_profile=True,
        default_profile_image=True,
        protected=True,
        verified=True,
        avatar="user.profile_image_url",
        tweets=[],
        score=0,
    )
    user_db.save()


def create_fake_twitter_user_collection():
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
        create_twitter_user(id=str(i), timestamp=datetime.utcnow() - ts)

    return len(up_to_date_ts), len(expired_ts)


def test_clean_database(client):
    num_new, num_old = create_fake_twitter_user_collection()
    assert TwitterUser.objects().count() == num_old + num_new
    clean_database(timedelta(days=settings.RESULT_MAX_AGE))

    users = TwitterUser.objects()
    assert users.count() == num_new
    for user in users:
        assert datetime.now(pytz.UTC) - user.timestamp < MAX_AGE
