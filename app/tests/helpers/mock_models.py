import json

import tweepy


class MockData:
    user_file = open("app/tests/data/user.json")
    data = json.load(user_file)
    user = None
    tweets = None
    user_file.close()

    @classmethod
    def user_info(cls):
        if cls.user is None:
            cls.user = tweepy.User(
                data={x: cls.data[x] for x in cls.data if x not in ["tweets"]}
            )
        return cls.user

    @classmethod
    def tweets_info(cls):
        if cls.tweets is None:
            cls.tweets = [tweepy.Tweet(data=x) for x in cls.data["tweets"]]
        return cls.tweets


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
        self.flatten_value = [] if "start_time" in kwargs else MockData.tweets_info()

    def flatten(self, *args, **kwargs):
        return self.flatten_value
