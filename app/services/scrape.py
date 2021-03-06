import calendar
import logging
from datetime import datetime, timedelta
from operator import attrgetter
from typing import List, Literal, Tuple, Union

import pytz  # type: ignore
import tweepy
from cachetools import TTLCache, cachedmethod
from cachetools.keys import hashkey
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.twitter import TimeSeries
from app.utils import Singleton

_logger = logging.getLogger(__name__)
TwitterID = Union[int, str]
Label = Literal[0, 1]


def _make_key(method_name: str):
    def method_key(_, *args, **kwargs):
        return hashkey(method_name, *args, **kwargs)

    return method_key


class TwitterScraper(metaclass=Singleton):
    _cache_func = attrgetter("_cache")

    def __init__(self) -> None:
        auth = tweepy.AppAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        self.api_v2 = tweepy.Client(
            bearer_token=auth._bearer_token, wait_on_rate_limit=True
        )
        self._cache: TTLCache = TTLCache(maxsize=1024, ttl=settings.TWEEPY_CACHE_TTL)

    @cachedmethod(cache=_cache_func, key=_make_key("get_user_by_username"))
    def get_user_by_username(self, username) -> tweepy.models.User:
        """
        Get details of Twitter user's information from given username.

        Args:
            username (string): The username of Twitter user got from input url.
        Return:
            tweepy.models.User: twitter user informations.
        """
        try:
            user = self.api.get_user(screen_name=username)
        except tweepy.NotFound:
            raise HTTPException(
                status_code=404, detail=f"User account @{username} not found"
            )
        except tweepy.Forbidden:
            raise HTTPException(
                status_code=403,
                detail=f"User account @{username} has been suspended",
            )
        else:
            return user

    @cachedmethod(cache=_cache_func, key=_make_key("get_user_by_id"))
    def get_user_by_id(self, twitter_id: TwitterID) -> tweepy.models.User:
        """Get Twitter user information from given ID."""
        try:
            user = self.api.get_user(user_id=twitter_id)
        except tweepy.NotFound:
            raise HTTPException(
                status_code=404, detail=f"User with ID {twitter_id} not found"
            )
        except tweepy.Forbidden:
            raise HTTPException(
                status_code=403,
                detail=f"User with ID {twitter_id} has been suspended",
            )
        else:
            return user

    @cachedmethod(cache=_cache_func, key=_make_key("get_tweet_info"))
    def get_tweet_info(self, user_id: TwitterID, tweets_num: int) -> List[tweepy.Tweet]:
        """
        Get list of a user's tweet (no replies, retweets)
        from given user's id and desired number of tweets.

        Args:
            user_id (string): The id of Twitter user.
            tweets_num (int): The number of tweets to get.
        Return:
            tweets (list<tweepy.Tweet>): List of user's tweets.
        """
        tweet_fields = ["created_at"]
        return list(
            tweepy.Paginator(
                self.api_v2.get_users_tweets,
                id=user_id,
                tweet_fields=tweet_fields,
                max_results=min(tweets_num, 100),
            ).flatten(limit=tweets_num)
        )

    @cachedmethod(cache=_cache_func, key=_make_key("get_frequency"))
    def get_frequency(self, user_id: TwitterID) -> Tuple[TimeSeries, TimeSeries]:
        """
        Get the frequency of user's tweets activity in 2 ways:
        Days of a week and Hours of a day.

        Args:
            user_id (string): The id of Twitter user.
        Return:
            dow_resp, hod_resp (TimeSeries, TimeSeries):
            Each list contains key-value pairs with:
            + key: day of week / hour of day when tweet was posted
            + value: number of tweets posted in the same time
        """
        tweet_fields = ["created_at"]
        timezone = pytz.timezone("Asia/Ho_Chi_Minh")
        day_of_week = [0] * 7
        hour_of_day = [0] * 24
        now = datetime.utcnow()
        start_time = now - timedelta(weeks=4)
        for tweet in tweepy.Paginator(
            self.api_v2.get_users_tweets,
            id=user_id,
            tweet_fields=tweet_fields,
            exclude=["replies", "retweets"],
            start_time=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            max_results=100,
        ).flatten():
            tweet_timestamp = tweet.created_at.astimezone(timezone)
            day_of_week[tweet_timestamp.weekday()] += 1
            hour_of_day[tweet_timestamp.hour] += 1

        logging.warn(sum(day_of_week))
        logging.warn(sum(hour_of_day))
        dow_resp = TimeSeries(
            time=list(calendar.day_abbr),
            value=day_of_week,
        )
        hod_resp = TimeSeries(
            time=[f"{h:02}:00" for h in range(24)],
            value=hour_of_day,
        )
        return dow_resp, hod_resp

    @cachedmethod(cache=_cache_func, key=_make_key("get_conversation"))
    def get_conversation(self, conversation_id: TwitterID) -> List[tweepy.Tweet]:
        return list(
            tweepy.Paginator(
                self.api_v2.search_recent_tweets,
                query=f"conversation_id:{conversation_id}",
                tweet_fields=["referenced_tweets", "public_metrics"],
            ).flatten()
        )
