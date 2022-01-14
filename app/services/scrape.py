from os import wait
import numpy as np
import pandas as pd
import tweepy  # type: ignore
from tweepy import TweepyException
from functools import lru_cache

from app.core.config import settings
from app.schemas.tweet_info import TweetInfoResponse


@lru_cache(maxsize=128)
class UserInfoScraper:
    def __init__(self, url_input) -> None:
        self.auth = tweepy.AppAuthHandler(
            settings.CONSUMER_KEY, settings.CONSUMER_SECRET
        )
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        # self.client = tweepy.Client(settings.BEARER_TOKEN, wait_on_rate_limit=True)
        self.user_url = url_input
        self.user_name = self.user_url.split("/")[3]
        try:
            self.user_api = self.api.get_user(screen_name=self.user_name)
        except:
            raise TweepyException(f"{self.user_name} - User not found!")

    def get_followers(self, followers_numbs):
        followers = []
        for follower in tweepy.Cursor(
            self.api.get_follower_ids, screen_name=self.user_name
        ).items(followers_numbs):
            followers.append(follower)

        return followers

    def get_followings(self, followings_numbs):
        followings = []
        for following in tweepy.Cursor(
            self.api.get_friend_ids, screen_name=self.user_name
        ).items(followings_numbs):
            followings.append(following)

        return followings

    def get_profile_info(self):
        profile_attribute = [
            "id_str",
            "name",
            "screen_name",
            "created_at",
            "followers_count",
            "friends_count",
            "profile_image_url",
            "profile_banner_url",
        ]

        profile_info = []
        for attribute in profile_attribute:
            profile_info.append(getattr(self.user_api, attribute, None))

        profile_info_df = pd.DataFrame(
            np.array(profile_info).reshape(1, len(profile_attribute)),
            columns=profile_attribute,
        )
        return profile_info_df

    def get_tweet_info(self, tweets_numbs):
        tweets = []
        for status in tweepy.Cursor(
            self.api.user_timeline,
            screen_name=self.user_name,
            exclude_replies=True,
            tweet_mode="extended",
        ).items(tweets_numbs):
            tweet_object = TweetInfoResponse(
                id=status.id_str, text=status.full_text, created_at=status.created_at
            )
            print(status.id_str)
            tweets.append(tweet_object)
        return tweets
