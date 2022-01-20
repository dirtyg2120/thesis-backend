from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.schemas.user_detail import UserDetailResponse
from app.schemas.user_info import UserInfoResponse
from app.services.scrape import TwitterScraper

router = APIRouter()


@router.get("/check", response_model=UserInfoResponse, name="user:get-data")
async def user_info_check(url: str, scraper: TwitterScraper = Depends()):
    if not url or url[:20] != "https://twitter.com/":
        raise HTTPException(status_code=400, detail="'url_input' argument is invalid!")

    username = url.split("/")[3]
    user_info = scraper.get_user_by_username(username)
    if user_info is None:
        raise HTTPException(status_code=404, detail=f"User @{username} does not exist")
    tweets_list = scraper.get_tweet_info(user_info.id_str, settings.TWEETS_NUMBER)

    response = UserInfoResponse(
        id=user_info.id_str,
        name=user_info.name,
        username=user_info.screen_name,
        created_at=user_info.created_at,
        is_real=False,
        followers_count=user_info.followers_count,
        followings_count=user_info.friends_count,
        avatar=user_info.profile_image_url,
        banner=user_info.profile_banner_url,
        tweets=tweets_list,
    )
    return response


@router.get("/detail", response_model=UserDetailResponse, name="user:get-detail")
async def user_detail_check(url: str, scraper: TwitterScraper = Depends()):
    if not url or url[:20] != "https://twitter.com/":
        raise HTTPException(status_code=400, detail="'url_input' argument is invalid!")

    username = url.split("/")[3]
    user_info = scraper.get_user_by_username(username)
    if user_info is None:
        raise HTTPException(status_code=404, detail=f"User @{username} does not exist")
    day_of_week, hour_of_day = scraper.get_frequency(user_info.id_str)

    return UserDetailResponse(day_of_week=day_of_week, hour_of_day=hour_of_day)
