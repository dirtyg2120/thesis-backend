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

    user_info = schemas.TwitterUser(
        id=user_db.twitter_id,
        name=user_db.name,
        username=user_db.username,
        created_at=user_db.created_at,
        followers_count=user_db.followers_count,
        followings_count=user_db.followings_count,
        avatar=user_db.avatar,
        banner=user_db.banner,
    )
    response = schemas.CheckResponse(is_real=False, user_info=user_info)
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

    user_info = schemas.TwitterUser(
        id=user_db.twitter_id,
        name=user_db.name,
        username=user_db.username,
        created_at=user_db.created_at,
        followers_count=user_db.followers_count,
        followings_count=user_db.followings_count,
        avatar=user_db.avatar,
        banner=user_db.banner,
    )
    response = schemas.DetailResponse(user_info=user_info, tweet_info=tweet_info)
    return response
