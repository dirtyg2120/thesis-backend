import logging

from app.core.config import settings
from app.models import Tweet, TwitterUser

from .ml import ML
from .scrape import TwitterScraper

_logger = logging.getLogger(__name__)


class BotChecker:
    def __init__(self):
        self.ml = ML()
        self.scraper = TwitterScraper()

    def check_account(self, username):
        user_db: TwitterUser = TwitterUser.objects(username=username).first()
        if user_db is None:
            _logger.info("This account is not exist in DB")
            user = self.scraper.get_user_by_username(username)
            recent_tweets = [
                Tweet(
                    tweet_id=str(tweet.id), text=tweet.text, created_at=tweet.created_at
                )
                for tweet in self.scraper.get_tweet_info(
                    user.id_str, settings.TWEETS_NUMBER
                )
            ]
            user_db = TwitterUser(
                twitter_id=user.id_str,
                name=user.name,
                username=user.screen_name,
                created_at=user.created_at,
                followers_count=user.followers_count,
                followings_count=user.friends_count,
                verified=user.verified,
                avatar=user.profile_image_url,
                banner=getattr(user, "profile_banner_url", None),
                tweets=recent_tweets,
                score=self.ml.get_analysis_result(user.screen_name),
            )
            user_db.save()

        return user_db
