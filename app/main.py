import uvicorn
from fastapi import FastAPI

from .api import api_router
from .core.config import settings


def get_application() -> FastAPI:
    # application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)
    application = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
    application.include_router(api_router, prefix=settings.API_PREFIX)

    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True, debug=False)
