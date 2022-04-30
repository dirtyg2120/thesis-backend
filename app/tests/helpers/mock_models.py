from functools import lru_cache
import json
from importlib.resources import open_text, read_text

import tweepy

from app.tests import data as test_data


@lru_cache
def get_mock_user():
    data = read_text(test_data, "user.json")
    parser = tweepy.parsers.ModelParser()
    api = tweepy.API()
    return parser.parse(data, api=api, payload_type='user')


@lru_cache
def get_mock_tweets():
    with open_text(test_data, "tweets.json") as f:
        data = json.load(f)
    return list(map(tweepy.Tweet, data))


class MockResponse:
    def __init__(self, status_code=None, json_data={}, reason="None"):
        self.status_code = status_code
        self.json_data = json_data
        self.reason = reason

    def json(self):
        return self.json_data


class MockPaginator:
    """
    This paginator returns:
    - Tweets if get all tweets (for TwitterScraper.get_tweet_info)
    - Nothing if get recent tweets (for TwitterScraper.get_frequency)
    """

    def __init__(self, *args, **kwargs):
        self.flatten_value = [] if "start_time" in kwargs else get_mock_tweets()

    def flatten(self, *args, **kwargs):
        return self.flatten_value
