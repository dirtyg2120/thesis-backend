from operator import attrgetter
from typing import List, Tuple

import pandas as pd
import tweepy  # type: ignore
from cachetools import TTLCache, cachedmethod
from cachetools.keys import hashkey
from fastapi import HTTPException

from app.core.config import settings
from app.models import TwitterUser
from app.schemas.tweet import TimeSeries


def _make_key(method_name: str):
    def method_key(_, *args, **kwargs):
        return hashkey(method_name, *args, **kwargs)

    return method_key


class TwitterScraper:
    _cache_func = attrgetter("_cache")

    def __init__(self) -> None:
        auth = tweepy.AppAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        self.api_v2 = tweepy.Client(
            bearer_token=auth._bearer_token, wait_on_rate_limit=True
        )
        self._cache: TTLCache = TTLCache(maxsize=1024, ttl=settings.TWEEPY_CACHE_TTL)

    @cachedmethod(cache=_cache_func, key=_make_key("get_user_by_username"))
    def get_user_by_username(self, username) -> TwitterUser:
        """
        Get details of Twitter user's information from given username.

        Args:
            username (string): The username of Twitter user got from input url.
        Return:
            myitems (schemas.TwitterUser): TwitterUser informations.
        """
        user_db = TwitterUser.objects(username=username).first()

        if user_db is None:
            print("This account is not exist in DB")
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
                print(type(user))
                user_db = TwitterUser(
                    twitter_id=user.id_str,
                    name=user.name,
                    username=user.screen_name,
                    created_at=user.created_at,
                    followers_count=user.followers_count,
                    followings_count=user.friends_count,
                    avatar=user.profile_image_url,
                    banner=getattr(user, "profile_banner_url", None),
                )

                user_db.save()

        return user_db

    def get_followers(self, followers_numbs):
        """
        Get list of Twitter user's followers.

        Args:
            followers_numbs (int): Number of followers to get.
        Return:
            followers (list<string>): List of followers' id.
        """
        followers = []
        for follower in tweepy.Cursor(
            self.api.get_follower_ids, screen_name=self.username
        ).items(followers_numbs):
            followers.append(follower)

        return followers

    def get_followings(self, followings_numbs):
        """
        Get list of Twitter user's followings.

        Args:
            followings_numbs (int): Number of followings to get.
        Return:
            followings (list<string>): List of followings' id.
        """
        followings = []
        for following in tweepy.Cursor(
            self.api.get_friend_ids, screen_name=self.username
        ).items(followings_numbs):
            followings.append(following)

        return followings

    @cachedmethod(cache=_cache_func, key=_make_key("get_tweet_info"))
    def get_tweet_info(self, user_id: str, tweets_num: int) -> List[tweepy.Tweet]:
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
        tweets = list(
            tweepy.Paginator(
                self.api_v2.get_users_tweets,
                id=user_id,
                tweet_fields=tweet_fields,
                exclude=["replies", "retweets"],
                max_results=min(tweets_num, 100),
            ).flatten(limit=tweets_num)
        )
        return tweets

    @cachedmethod(cache=_cache_func, key=_make_key("get_frequency"))
    def get_frequency(self, user_id: str) -> Tuple[TimeSeries, TimeSeries]:
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
        timezone = "Asia/Ho_Chi_Minh"
        now = pd.Timestamp.now(tz=timezone)
        day_of_week = pd.Series(
            index=pd.period_range(end=now, periods=7, freq="D"), dtype=int
        )
        start_day_of_week = day_of_week.index[0].start_time.tz_localize(timezone)
        hour_of_day = pd.Series(
            index=pd.period_range(end=now, periods=24, freq="H"), dtype=int
        )
        start_hour_of_day = hour_of_day.index[0].start_time.tz_localize(timezone)

        for tweet in tweepy.Paginator(
            self.api_v2.get_users_tweets,
            id=user_id,
            tweet_fields=tweet_fields,
            exclude=["replies", "retweets"],
            start_time=start_day_of_week.astimezone("UTC").strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            max_results=100,
        ).flatten():
            tweet_timestamp = pd.Timestamp(tweet.created_at).tz_convert(timezone)
            day_of_week[tweet_timestamp] += 1

            if tweet_timestamp >= start_hour_of_day:
                # Only count tweets in the last 24 hours
                hour_of_day[tweet_timestamp] += 1

        dow_resp = TimeSeries(
            time=day_of_week.index.strftime("%a").tolist(),
            value=day_of_week.tolist(),
        )
        hod_resp = TimeSeries(
            time=hour_of_day.index.strftime("%H:%M").tolist(),
            value=hour_of_day.tolist(),
        )
        return dow_resp, hod_resp
