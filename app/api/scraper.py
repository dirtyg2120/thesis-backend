from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.core.config import settings
from app.services.scrape import TwitterScraper

router = APIRouter()


@router.get("/check", response_model=schemas.CheckResponse, name="user:get-data")
async def twitter_user_info_check(url: str, scraper: TwitterScraper = Depends()):
    # Validate input url
    if url[:20] == "https://twitter.com/":
        username = url.split("/")[3]
    elif url[:12] == "twitter.com/":
        username = url.split("/")[1]
    elif url:
        username = url
    else:
        raise HTTPException(status_code=400, detail="'url' argument is invalid!")

    twitter_user_info = scraper.get_twitter_user_by_username(username)
    response = schemas.CheckResponse(is_real=False, twitter_user_info=twitter_user_info)
    return response


@router.get("/detail", response_model=schemas.DetailResponse, name="user:get-detail")
async def twitter_user_detail_check(username: str, scraper: TwitterScraper = Depends()):

    twitter_user_info = scraper.get_twitter_user_by_username(username)

    recent_tweets = scraper.get_tweet_info(
        twitter_user_info["twitter_id"], settings.TWEETS_NUMBER
    )
    day_of_week, hour_of_day = scraper.get_frequency(twitter_user_info["twitter_id"])
    tweet_info = schemas.TweetInfo(
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        recent_tweets=recent_tweets,
    )

    response = schemas.DetailResponse(
        twitter_user_info=twitter_user_info, tweet_info=tweet_info
    )
    return response
