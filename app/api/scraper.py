from fastapi import APIRouter, HTTPException

from app.models.userinfo import UserInfoResponse
from app.services.scrape import UserInfoScraper

router = APIRouter()


@router.get("/check", response_model=UserInfoResponse, name="user:get-data")
async def user_info_check(url_input: str):
    if not url_input:
        raise HTTPException(status_code=404, detail="'url_input' argument invalid!")
    try:
        user = UserInfoScraper(url_input)
        user_info = user.get_profile_info()
        tweets_list = user.get_tweets(10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {e}")

    response = UserInfoResponse(
        id=user_info["id"].iloc[0],
        name=user_info["name"].iloc[0],
        screen_name=user_info["screen_name"].iloc[0],
        created_at=user_info["created_at"].iloc[0],
        is_real=False,
        followers_count=user_info["followers_count"].iloc[0],
        followings_count=user_info["friends_count"].iloc[0],
        banner=user_info["profile_background_image_url"].iloc[0],
        avatar=user_info["profile_image_url"].iloc[0],
        tweets=tweets_list,
    )
    return response
