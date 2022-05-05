from datetime import timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from mongoengine import connect, disconnect
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

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

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT],
    enabled=settings.PYTHON_ENV == "production",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router)


@app.on_event("startup")
def connect_db():
    is_mock = settings.PYTHON_ENV == "test"
    connect(
        settings.MONGO_DB,
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
        tz_aware=True,
        is_mock=is_mock,
    )


@app.on_event("startup")
@repeat_every(seconds=settings.RESULT_MAX_AGE * 86400)
def clear_db():
    clean_database(timedelta(days=settings.RESULT_MAX_AGE))


@app.on_event("shutdown")
def disconnect_db():
    disconnect()


if __name__ == "__main__":
    import uvicorn  # type: ignore

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["handlers"]["database"] = {
        "class": "app.services.log_db_handler.LogDBHandler"
    }
    log_config["loggers"]["app"] = {
        "level": "INFO",
        "handlers": ["default", "database"],
    }
    log_config["loggers"]["uvicorn.access"]["handlers"].append("database")

    uvicorn.run(
        "app.main:app",
        port=settings.PORT,
        reload=settings.PYTHON_ENV == "development",
        debug=False,
        log_config=log_config,
    )
