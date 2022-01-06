import uvicorn  # type: ignore
from fastapi import FastAPI

from .api import api_router
from .core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.include_router(api_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True, debug=False)
