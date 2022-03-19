import json

import tweepy


class MockData:
    user_file = open("app/tests/data/user.json")
    data = json.load(user_file)
    user_file.close()

    @classmethod
    def user_info(self):
        exclude = ["tweets"]
        return tweepy.User(
            data={x: MockData.data[x] for x in MockData.data if x not in exclude}
        )

    @classmethod
    def tweets(self):
        return [tweepy.Tweet(data=x) for x in MockData.data["tweets"]]


class MockResponse:
    def __init__(self, status_code=None, json_data={}, reason="None"):
        self.status_code = status_code
        self.json_data = json_data
        self.reason = reason

    def json(self):
        return self.json_data
