from urllib.parse import urlparse

from fastapi import HTTPException


def parse_twitter_url(url: str) -> str:
    """Parse URL and return Twitter username."""
    parsed = urlparse(url)

    if parsed.netloc != "twitter.com":
        raise HTTPException(400, "'url' argument is invalid!")

    url_parts = parsed.path.split("/")[1:]
    if len(url_parts) == 0:
        raise HTTPException(400, "'url' argument is invalid!")

    return url_parts[0]
