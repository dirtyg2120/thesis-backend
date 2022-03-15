from typing import Literal, Tuple
from urllib.parse import urlparse


def parse_url(url: str) -> Tuple[Literal["user", "tweet"], str]:
    parsed = urlparse(url)

    if parsed.netloc != "twitter.com":
        raise ValueError("Invalid Twitter URL")

    url_parts = parsed.path.split("/")[1:]
    if url_parts[1] == "status":
        tweet_id = url_parts[2]
        return "tweet", tweet_id
    else:
        username = url_parts[0]
        return "user", username
