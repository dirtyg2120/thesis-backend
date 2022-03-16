import logging

from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.core.config import settings
from app.models import TwitterUser
from app.services.ml import ML
from app.services.scrape import TwitterScraper

_logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/check", response_model=schemas.CheckResponse, name="user:get-data")
def user_info_check(
    url: str, scraper: TwitterScraper = Depends(), ml_service: ML = Depends()
) -> schemas.CheckResponse:
    # Validate input url
    if url[:20] == "https://twitter.com/":
        username = url.split("/")[3]
    elif url[:12] == "twitter.com/":
        username = url.split("/")[1]
    elif url != "" and "/" not in url:
        username = url
    else:
        raise HTTPException(status_code=400, detail="'url' argument is invalid!")

    user_db: TwitterUser = TwitterUser.objects(username=username).first()
    if user_db is None:
        _logger.info("This account is not exist in DB")
        user = scraper.get_user_by_username(username)
        recent_tweets = scraper.get_tweet_info(user.id_str, settings.TWEETS_NUMBER)
        user_db = TwitterUser(
            twitter_id=user.id_str,
            name=user.name,
            username=user.screen_name,
            created_at=user.created_at,
            followers_count=user.followers_count,
            followings_count=user.friends_count,
            verified=user.verified,
            avatar=user.profile_image_url,
            banner=getattr(user, "profile_banner_url", None),
            tweets=recent_tweets,
            score=ml_service.get_analysis_result(user.screen_name),
        )
        user_db.save()

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

    user_resp = user_info_check(username)
    user_db: TwitterUser = TwitterUser.objects(username=username).first()

    recent_tweets = user_db.tweets
    recent_tweets_response = [tweet.to_response() for tweet in recent_tweets]

    day_of_week, hour_of_day = scraper.get_frequency(user_db["twitter_id"])
    tweet_info = schemas.TweetInfo(
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        recent_tweets=recent_tweets_response,
    )

    response = schemas.DetailResponse(
        user_info=user_resp.user_info, tweet_info=tweet_info, score=user_resp.score
    )
    return response
