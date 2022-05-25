import logging

from networkx.readwrite import json_graph

from app.models import BotPrediction
from app.models.twitter import TwitterInfo, User
from app.utils import Singleton

from .ml import ML
from .scrape import TwitterScraper

_logger = logging.getLogger(__name__)


class BotChecker(metaclass=Singleton):
    def __init__(self):
        self._ml_service = ML()
        self._scraper = TwitterScraper()

    def check_account(self, username):
        user = self._scraper.get_user_by_username(username)
        prediction_db: BotPrediction = BotPrediction.objects(
            user_id=user.id_str,
        ).first()
        if prediction_db is None:
            _logger.info("This account is not exist in DB")
            # self._ml_service = ML()
            score, user, tweet_graph = self._ml_service.get_analysis_result(username)
            tweet_graph = json_graph.node_link_data(tweet_graph)
            twitter_info = TwitterInfo(
                user_id=user.id_str,
                user=User(
                    twitter_id=user.id_str,
                    name=user.name,
                    screen_name=user.screen_name.lower(),
                    created_at=user.created_at,
                    statuses_count=user.statuses_count,
                    followers_count=user.followers_count,
                    friends_count=user.friends_count,
                    favourites_count=user.favourites_count,
                    listed_count=user.listed_count,
                    default_profile=user.default_profile,
                    default_profile_image=user.default_profile_image,
                    protected=user.protected,
                    verified=user.verified,
                    avatar=user.profile_image_url,
                    banner=getattr(user, "profile_banner_url", None),
                    description=user.description,
                ),
                tweets=tweet_graph["nodes"],
                tweet_relation=tweet_graph["links"],
            ).save()
            prediction_db = BotPrediction(
                score=score,
                user_id=user.id_str,
                twitter_info=twitter_info,
            ).save()

        return prediction_db
