from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.core.config import settings
from app.services.scrape import TwitterScraper

router = APIRouter()


@router.get("/check", response_model=schemas.CheckResponse, name="user:get-data")
async def user_info_check(url: str, scraper: TwitterScraper = Depends()):
    if not url or url[:20] != "https://twitter.com/":
        raise HTTPException(status_code=400, detail="'url_input' argument is invalid!")

    username = url.split("/")[3]
    user_info = scraper.get_user_by_username(username)
    if user_info is None:
        raise HTTPException(status_code=404, detail=f"User @{username} does not exist")

    response = schemas.CheckResponse(is_real=False, user_info=user_info)
    return response


@router.get("/detail", response_model=schemas.DetailResponse, name="user:get-detail")
async def user_detail_check(url: str, scraper: TwitterScraper = Depends()):
    if not url or url[:20] != "https://twitter.com/":
        raise HTTPException(status_code=400, detail="'url_input' argument is invalid!")

    username = url.split("/")[3]
    user_info = scraper.get_user_by_username(username)
    if user_info is None:
        raise HTTPException(status_code=404, detail=f"User @{username} does not exist")

    recent_tweets = scraper.get_tweet_info(user_info.id, settings.TWEETS_NUMBER)
    day_of_week, hour_of_day = scraper.get_frequency(user_info.id)
    tweet_info = schemas.TweetInfo(
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        recent_tweets=recent_tweets,
    )

    response = schemas.DetailResponse(user_info=user_info, tweet_info=tweet_info)
    return response
