from fastapi import APIRouter

from app.core.config import settings

from . import auth, scraper

api_router = APIRouter()
api_router.include_router(scraper.router, tags=["scraper"], prefix=settings.API_PREFIX)
api_router.include_router(auth.router, tags=["auth"], prefix=settings.AUTH_PREFIX)
