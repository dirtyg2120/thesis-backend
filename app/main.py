import uvicorn  # type: ignore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect, disconnect

from .api import api_router
from .core.config import settings

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
    )


@app.on_event("shutdown")
def disconnect_db():
    disconnect()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, debug=False)
