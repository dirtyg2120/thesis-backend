from fastapi import APIRouter

from . import scraper

api_router = APIRouter()
api_router.include_router(scraper.router, tags=["scraper"])
