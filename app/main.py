from typing import Optional

from fastapi import FastAPI, applications


from logging import debug
import uvicorn
from fastapi import FastAPI
from api.router import router as api_router

from core.config import PROJECT_NAME, API_PREFIX, VERSION
def get_application() -> FastAPI:
    # application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)
    application = FastAPI(title=PROJECT_NAME, version=VERSION)
    application.include_router(api_router, prefix=API_PREFIX)
    
    return application

app = get_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port = 8080, reload = True, debug = False)
