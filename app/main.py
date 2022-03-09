from datetime import timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from mongoengine import connect, disconnect

from .api import api_router
from .core.config import settings
from .services.clean_database import clean_database

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def connect_db():
    connect(
        settings.MONGO_DB,
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
        tz_aware=True,
    )


@app.on_event("startup")
@repeat_every(seconds=settings.RESULT_MAX_AGE * 86400, raise_exceptions=True)
def clear_db():
    clean_database(timedelta(days=settings.RESULT_MAX_AGE))


@app.on_event("shutdown")
def disconnect_db():
    disconnect()


if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, debug=False)
