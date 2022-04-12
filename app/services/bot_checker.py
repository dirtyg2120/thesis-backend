import logging

from fastapi import Depends

from app.core.config import settings
from app.models import BotPrediction, Tweet

from .ml import ML
from .scrape import TwitterScraper

_logger = logging.getLogger(__name__)


class BotChecker:
    def __init__(self, ml: ML = Depends(), scraper: TwitterScraper = Depends()):
        self._ml_service = ml
        self._scraper = scraper

    def check_account(self, username):
        user_db: BotPrediction = BotPrediction.objects(username=username).first()
        if user_db is None:
            _logger.info("This account is not exist in DB")
            user = self._scraper.get_user_by_username(username)
            recent_tweets = [
                Tweet(
                    tweet_id=str(tweet.id), text=tweet.text, created_at=tweet.created_at
                )
                for tweet in self._scraper.get_tweet_info(
                    user.id_str, settings.TWEETS_NUMBER
                )
            ]
            user_db = BotPrediction(
                twitter_id=user.id_str,
                tweets_count=user.statuses_count,
                name=user.name,
                username=user.screen_name,
                created_at=user.created_at,
                followers_count=user.followers_count,
                followings_count=user.friends_count,
                favourites_count=user.favourites_count,
                listed_count=user.listed_count,
                default_profile=user.default_profile,
                default_profile_image=user.default_profile_image,
                protected=user.protected,
                verified=user.verified,
                avatar=user.profile_image_url,
                banner=getattr(user, "profile_banner_url", None),
                tweets=recent_tweets,
                score=self._ml_service.get_analysis_result(user.screen_name),
            )
            user_db.save()

        return user_db
