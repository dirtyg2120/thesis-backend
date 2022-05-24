import logging

from fastapi import Depends
from networkx.readwrite import json_graph

from app.models import BotPrediction, User

from .ml import ML
from .scrape import TwitterScraper

_logger = logging.getLogger(__name__)


class BotChecker:
    def __init__(self, ml: ML = Depends(), scraper: TwitterScraper = Depends()):
        self._ml_service = ml
        self._scraper = scraper

    def check_account(self, username):
        prediction_db: BotPrediction = BotPrediction.objects(
            user__screen_name=username.lower()
        ).first()
        if prediction_db is None:
            _logger.info("This account is not exist in DB")
            score, user, tweet_graph = self._ml_service.get_analysis_result(username)
            tweet_graph = json_graph.node_link_data(tweet_graph)
            prediction_db = BotPrediction(
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
                tweets={"graph": tweet_graph["graph"], "nodes": tweet_graph["nodes"]},
                score=score,
                user_id=user.id_str,
            ).save()

        return prediction_db
