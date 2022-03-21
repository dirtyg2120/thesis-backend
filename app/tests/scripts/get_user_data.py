import json
import sys
from datetime import datetime

import tweepy  # type: ignore

from app.core.config import settings

auth = tweepy.AppAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
api_v2 = tweepy.Client(bearer_token=auth._bearer_token, wait_on_rate_limit=True)

if len(sys.argv) != 3:
    sys.exit("python -m app.tests.script.<current-file> <username> <tweet_num>")

username = sys.argv[1]
tweets_num = int(sys.argv[2])

user = api.get_user(screen_name=username)
tweets = list(
    map(
        lambda tweet: tweet.data,
        list(
            tweepy.Paginator(
                api_v2.get_users_tweets,
                id=user.id_str,
                tweet_fields=["created_at"],
                exclude=["replies", "retweets"],
                max_results=min(tweets_num, 100),
            ).flatten(limit=tweets_num)
        ),
    )
)


def format_time(twitter_time_str):
    return datetime.strftime(
        datetime.strptime(twitter_time_str, "%a %b %d %H:%M:%S +0000 %Y"),
        "%Y-%m-%dT%H:%M:%S.%fZ",
    )


with open(f"./app/tests/data/{username}.json", "w") as out:
    json_output = user._json
    json_output["username"] = username
    json_output["created_at"] = format_time(json_output["created_at"])
    json_output["tweets"] = tweets
    json.dump(json_output, out)
