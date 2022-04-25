import json
import os
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

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
    prediction = bot_checker.check_account(username)

    response = schemas.CheckResponse(
        user_info=prediction.user.to_user_info(),
        score=prediction.score,
    )
    return response


@router.get("/detail", response_model=schemas.DetailResponse, name="user:get-detail")
def user_detail_check(
    url: str, bot_checker: BotChecker = Depends(), scraper: TwitterScraper = Depends()
):
    if url == "":
        raise HTTPException(400, "'url' argument is invalid!")

    username = get_twitter_username(url)
    prediction = bot_checker.check_account(username)

    recent_tweets = scraper.get_tweet_info(prediction.user.twitter_id, 50)
    recent_tweets_response = [
        schemas.TweetResponse(
            id=str(tweet.id), text=tweet.text, created_at=tweet.created_at
        )
        for tweet in recent_tweets
    ]

    day_of_week, hour_of_day = scraper.get_frequency(prediction.user.twitter_id)
    tweet_info = schemas.TweetInfo(
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        recent_tweets=recent_tweets_response,
    )

    response = schemas.DetailResponse(
        user_info=prediction.user.to_user_info(),
        tweet_info=tweet_info,
        score=prediction.score,
    )
    return response


@router.get("/export", name="user:export-detail")
def export_profile(
    url: str, bg_tasks: BackgroundTasks, scraper: TwitterScraper = Depends()
):
    if url == "":
        raise HTTPException(400, "'url' argument is invalid!")

    username = get_twitter_username(url)
    full_details = scraper.get_full_details(username, 3)

    file_path = f"{full_details.screen_name}.json"
    with open(file_path, "w") as f:
        full_details_str = (
            str(full_details._json)
            .replace('"', '\\"')
            .replace("'", '"')
            .replace(': \\"', ': "')
            .replace('\\",', '",')
            .replace("None", "null")
            .replace("True", "true")
            .replace("False", "false")
        )
        full_details_str = re.sub(r'(\w)"(\w)', r"\1'\2", full_details_str)
        mydata = json.loads(full_details_str)
        f.write(json.dumps(mydata, indent=4))

    bg_tasks.add_task(remove_file, file_path)

    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="application/json",
            filename=f"{full_details.screen_name}.json",
        )


def remove_file(path: str) -> None:
    os.remove(path)
