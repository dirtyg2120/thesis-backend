from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.encoders import jsonable_encoder

from app import schemas
from app.core.config import settings
from app.services.scrape import TwitterScraper
from app.database.database import MongoDBPipeline

router = APIRouter()
db = MongoDBPipeline()


@router.get("/check", response_model=schemas.CheckResponse, name="user:get-data")
async def user_info_check(url: str, scraper: TwitterScraper = Depends()):
    # Validate input url
    if url[:20] == "https://twitter.com/":
        username = url.split("/")[3]
    elif url[:12] == "twitter.com/":
        username = url.split("/")[1]
    elif url:
        username = url
    else:
        raise HTTPException(status_code=400, detail="'url' argument is invalid!")

    user_info = scraper.get_user_by_username(username)
    response = schemas.CheckResponse(is_real=False, user_info=user_info)
    return response


@router.get("/detail", response_model=schemas.DetailResponse, name="user:get-detail")
async def user_detail_check(url: str, scraper: TwitterScraper = Depends()):
    # Validate input url
    if url[:20] == "https://twitter.com/":
        username = url.split("/")[3]
    elif url[:12] == "twitter.com/":
        username = url.split("/")[1]
    elif url:
        username = url
    else:
        raise HTTPException(status_code=400, detail="'url' argument is invalid!")

    user_info = scraper.get_user_by_username(username)

    recent_tweets = scraper.get_tweet_info(user_info.id, settings.TWEETS_NUMBER)
    day_of_week, hour_of_day = scraper.get_frequency(user_info.id)
    tweet_info = schemas.TweetInfo(
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        recent_tweets=recent_tweets,
    )

    response = schemas.DetailResponse(user_info=user_info, tweet_info=tweet_info)
    return response


@router.post("/profile", response_description="Profile data added into the database")
async def add_profile_data(profile: schemas.User = Body(...)):
    profile = jsonable_encoder(profile)
    db.add_profile(profile)
    return {"profile added successfully."}


@router.get("/profile", response_description="Profiles retrieved")
async def get_profiles():
    profiles = db.retrieve_profiles()
    return profiles


@router.get("/profile/{id}", response_description="Profile data retrieved")
async def get_profile_data(id):
    profile = db.retrieve_profile(id)
    if profile:
        return profile
    else:
        raise {"Profile doesn't exist."}
        # raise ErrorResponseModel("An error occured.", 404, "Profile doesn't exist.")
