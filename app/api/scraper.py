from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.user_detail import UserDetailResponse
from app.schemas.user_info import UserInfoResponse
from app.services.scrape import UserInfoScraper

router = APIRouter()


@router.get("/check", response_model=UserInfoResponse, name="user:get-data")
async def user_info_check(url: str):
    if not url or url[:20] != "https://twitter.com/":
        raise HTTPException(status_code=404, detail="'url_input' argument is invalid!")
    try:
        username = url.split("/")[3]
        user = UserInfoScraper(username)
        user_info = user.get_profile_info()
        tweets_list = user.get_tweet_info(settings.TWEETS_NUMBER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {e}")

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
async def user_detail_check(url: str):
    if not url or url[:20] != "https://twitter.com/":
        raise HTTPException(status_code=404, detail="'url_input' argument is invalid!")
    try:
        user = UserInfoScraper(url)
        day_of_week, hour_of_day = user.get_frequency()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {e}")

    return UserDetailResponse(day_of_week=day_of_week, hour_of_day=hour_of_day)
