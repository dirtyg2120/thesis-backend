from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd
import tweepy
from fastapi import Depends

import model

from .scrape import TwitterID, TwitterScraper


def _find_replies_in_conversation(tweet_id: int, conversation: List[tweepy.Tweet]):
    replies = []
    for tweet in conversation:
        for reference_tweet in tweet.referenced_tweets:
            if reference_tweet.type == "replied_to" and reference_tweet.id == tweet_id:
                replies.append(
                    {
                        "id": tweet.id,
                        "text": tweet.text,
                        "parent_id": tweet_id,
                    }
                )
                break
    return replies


class ML:
    def __init__(self, scraper: TwitterScraper = Depends()):
        self._scraper = scraper
        self._inference = model.Inference()

    def train(self):
        # TODO: for train / re-train purpose
        pass

    def get_analysis_result(self, username: str) -> float:
        user_api = self._scraper.get_user_by_username(username)
        user = self._make_ml_user(user_api)
        tweets = self._get_ml_tweets(user_api.id)
        return self._inference.predict(user, tweets)

    def _get_ml_tweets(self, user_id: TwitterID):
        tweets = []
        # NOTE: Can only fetch tweets in a conversation in last 7 days
        # without Academic Research access
        duration = timedelta(days=7)
        last_week = datetime.utcnow() - duration
        for tweet in tweepy.Paginator(
            self._scraper.api_v2.get_users_tweets,
            id=user_id,
            tweet_fields="conversation_id",
            exclude=["replies", "retweets"],
            start_time=last_week.strftime("%Y-%m-%dT%H:%M:%SZ"),
            max_results=100,
        ).flatten():
            tweets.append({"id": tweet.id, "text": tweet.text, "parent_id": 0})

            if not tweet.text.startswith("RT @"):
                # Not a retweet
                conversation = self._scraper.get_conversation(tweet.conversation_id)
                replies = _find_replies_in_conversation(tweet.id, conversation)
                # Fetch 2nd level tweets
                for reply in replies:
                    tweets.extend(_find_replies_in_conversation(tweet.id, conversation))
                    tweets.extend(self._get_retweets(tweet.id))
                tweets.extend(replies)
                tweets.extend(self._get_retweets(tweet.id))

        df = pd.DataFrame.from_records(tweets, columns=["id", "text", "parent_id"])
        df = df.astype({"id": np.uint64, "parent_id": np.uint64})
        return df

    def _make_ml_user(self, user_api: tweepy.models.User):
        user_fields = [
            "created_at",
            "default_profile",
            "default_profile_image",
            "description",
            "favourites_count",
            "followers_count",
            "friends_count",
            "listed_count",
            "name",
            "protected",
            "screen_name",
            "statuses_count",
            "verified",
        ]
        user = {"updated": datetime.utcnow()}
        for field in user_fields:
            user[field] = getattr(user_api, field)
        return user

    def _get_retweets(self, tweet_id: TwitterID):
        retweets = self._scraper.api.get_retweets(tweet_id, trim_user=True)
        return [
            {"id": tweet.id, "text": tweet.text, "parent_id": tweet_id}
            for tweet in retweets
        ]
