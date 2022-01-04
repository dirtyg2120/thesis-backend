from fastapi import APIRouter
from fastapi.routing import APIRoute

from api import scraper

router = APIRouter()
router.include_router(scraper.router, tags = ["scraper"])