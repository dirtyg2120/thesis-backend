import numpy as np
import pandas as pd
import tweepy  # type: ignore
from tweepy import TweepyException

from app.core.config import settings


class UserInfoScraper:
    def __init__(self, url_input) -> None:
        self.auth = tweepy.AppAuthHandler(
            settings.CONSUMER_KEY, settings.CONSUMER_SECRET
        )
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        self.user_url = url_input
        self.user_name = self.user_url.split("/")[3]

    def get_followers(self, followers_numbs):
        followers = []
        for follower in tweepy.Cursor(
            self.api.get_follower_ids, screen_name=self.user_name
        ).items(followers_numbs):
            followers.append(follower)

        # followers_df = pd.DataFrame(followers)
        return followers

    def get_followings(self, followings_numbs):
        followings = []
        for following in tweepy.Cursor(
            self.api.get_friend_ids, screen_name=self.user_name
        ).items(followings_numbs):
            followings.append(following)

        # followings_df = pd.DataFrame(followings)
        return followings

    def get_profile_info(self):
        try:
            user_api = self.api.get_user(screen_name=self.user_name)
        except:
            raise TweepyException(f"{self.user_name} - User not found!")

        columns = [
            "id",
            "name",
            "screen_name",
            "created_at",
            "followers_count",
            "friends_count",
            "profile_background_image_url",
            "profile_image_url",
        ]

        profile_info = []
        for attribute in columns:
            profile_info.append(getattr(user_api, attribute))

        profile_info_df = pd.DataFrame(
            np.array(profile_info).reshape(1, len(columns)), columns=columns
        )
        return profile_info_df

    def get_tweets(self, tweets_numbs):
        tweets = []
        for status in tweepy.Cursor(
            self.api.user_timeline, screen_name=self.user_name, exclude_replies=True
        ).items(tweets_numbs):
            tweets.append(status.text)
        return tweets
