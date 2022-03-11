from datetime import datetime
from typing import List
from app.schemas.tweet import Tweet
from app.schemas.twitter_user import TwitterUser


class AccountReport(TwitterUser):
    tweets: List[Tweet]
    scrape_date: datetime
    reset_date: datetime
    report_count: int
