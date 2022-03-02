from fastapi import APIRouter

from . import scraper
from . import auth
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(scraper.router, tags=["scraper"], prefix=settings.API_PREFIX)
api_router.include_router(auth.router, tags=["auth"], prefix=settings.AUTH_PREFIX)
