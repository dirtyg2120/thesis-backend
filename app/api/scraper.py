from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.services.scrape import TwitterScraper

router = APIRouter()


@router.get("/check", response_model=schemas.CheckResponse, name="user:get-data")
def user_info_check(url: str, scraper: TwitterScraper = Depends()):
    # Validate input url
    if url[:20] == "https://twitter.com/":
        username = url.split("/")[3]
    elif url[:12] == "twitter.com/":
        username = url.split("/")[1]
    elif url != "" and "/" not in url:
        username = url
    else:
        raise HTTPException(status_code=400, detail="'url' argument is invalid!")

    user_db = scraper.get_user_by_username(username)

    response = schemas.CheckResponse(
        score=user_db.score, user_info=user_db.to_response()
    )
    return response


@router.get("/detail", response_model=schemas.DetailResponse, name="user:get-detail")
def user_detail_check(url: str, scraper: TwitterScraper = Depends()):
    # Validate input url
    if url[:20] == "https://twitter.com/":
        username = url.split("/")[3]
    elif url[:12] == "twitter.com/":
        username = url.split("/")[1]
    elif url != "" and "/" not in url:
        username = url
    else:
        raise HTTPException(status_code=400, detail="'url' argument is invalid!")

    user_db = scraper.get_user_by_username(username)

    recent_tweets = user_db.tweets
    recent_tweets_response = [tweet.to_response() for tweet in recent_tweets]

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
