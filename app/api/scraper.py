from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.services.bot_checker import BotChecker
from app.services.scrape import TwitterScraper
from app.services.url_parser import get_twitter_username

router = APIRouter()


@router.get("/check", response_model=schemas.CheckResponse, name="user:get-data")
def user_info_check(url: str, bot_checker: BotChecker = Depends()):
    if url == "":
        raise HTTPException(400, "'url' argument is invalid!")

    username = get_twitter_username(url)
    user_db = bot_checker.check_account(username)

    response = schemas.CheckResponse(
        score=user_db.score, user_info=user_db.to_response()
    )
    return response


@router.get("/detail", response_model=schemas.DetailResponse, name="user:get-detail")
def user_detail_check(
    url: str, bot_checker: BotChecker = Depends(), scraper: TwitterScraper = Depends()
):
    if url == "":
        raise HTTPException(400, "'url' argument is invalid!")

    username = get_twitter_username(url)

    user_db = scraper.get_user_by_username(username)

    recent_tweets = scraper.get_tweet_info(user_db.twitter_id, 50)
    recent_tweets_response = [
        schemas.TweetResponse(
            id=tweet.id_str, text=tweet.text, created_at=tweet.created_at
        )
        for tweet in recent_tweets
    ]

    day_of_week, hour_of_day = scraper.get_frequency(user_db["twitter_id"])
    tweet_info = schemas.TweetInfo(
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        recent_tweets=recent_tweets_response,
    )

    response = schemas.DetailResponse(
        user_info=user_db.to_response(), tweet_info=tweet_info, score=user_db.score
    )
    return response
