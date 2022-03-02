from fastapi import APIRouter

from . import auth

auth_router = APIRouter()
auth_router.include_router(auth.router, tags=["auth"])
