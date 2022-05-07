import logging

from fastapi import Depends

from app.models import BotPrediction

from .ml import ML
from .scrape import TwitterScraper

_logger = logging.getLogger(__name__)


class BotChecker:
    def __init__(self, ml: ML = Depends(), scraper: TwitterScraper = Depends()):
        self._ml_service = ml
        self._scraper = scraper

    def check_account(self, username):
        user = self._scraper.get_user_by_username(username)

        prediction_db: BotPrediction = BotPrediction.objects(
            user_id=user.id_str
        ).first()
        if prediction_db is None:
            _logger.info("This account is not exist in DB")
            prediction_db = BotPrediction(
                user_id=user.id_str,
                score=self._ml_service.get_analysis_result(username),
            )
            prediction_db.save()

        return prediction_db
