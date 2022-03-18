from typing import Literal, Tuple
from urllib.parse import urlparse

from fastapi import HTTPException


def parse_twitter_url(url: str) -> Tuple[Literal["user", "tweet"], str]:
    parsed = urlparse(url)

    if parsed.netloc != "twitter.com":
        raise HTTPException(400, "'url' argument is invalid!")

    url_parts = parsed.path.split("/")[1:]
    if len(url_parts) >= 3 and url_parts[1] == "status":
        tweet_id = url_parts[2]
        return "tweet", tweet_id
    elif len(url_parts) >= 1:
        username = url_parts[0]
        return "user", username
    else:
        raise HTTPException(400, "'url' argument is invalid!")
