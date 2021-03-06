from fastapi import APIRouter, HTTPException

from app import schemas
from app.core.config import settings
from app.services.bot_checker import BotChecker
from app.services.scrape import TwitterScraper
from app.services.url_parser import get_twitter_username

router = APIRouter()


@router.get("/check", response_model=schemas.CheckResponse, name="user:get-data")
def user_info_check(url: str):
    if url == "":
        raise HTTPException(400, "'url' argument is invalid!")

    bot_checker = BotChecker()
    username = get_twitter_username(url)
    prediction = bot_checker.check_account(username)

    response = schemas.CheckResponse(
        user_info=prediction.twitter_info.user, score=prediction.score
    )
    return response


@router.get("/detail", response_model=schemas.DetailResponse, name="user:get-detail")
def user_detail_check(url: str):
    bot_checker = BotChecker()
    scraper = TwitterScraper()
    if url == "":
        raise HTTPException(400, "'url' argument is invalid!")

    username = get_twitter_username(url)
    prediction = bot_checker.check_account(username)

    recent_tweets = scraper.get_tweet_info(prediction.user_id, settings.TWEETS_NUMBER)

    day_of_week, hour_of_day = scraper.get_frequency(prediction.user_id)
    tweet_info = schemas.TweetInfo(
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        recent_tweets=recent_tweets,
    )

    response = schemas.DetailResponse(
        user_info=prediction.twitter_info.user,
        tweet_info=tweet_info,
        score=prediction.score,
    )
    return response
