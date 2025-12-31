import sys
import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from Helper.ConfigHelper import ConfigHelper
from Helper.Logger import setup_custom_logger

# this is required to work within the docker container
sys.path.append('/app/api/')

os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

# noinspection PyPep8
from Routers import strava, developer, lifecycle, snapshots, execute, frontend

description = """
This is a vestaboard server implementation which organizes the vestaboard related content within scenes. 🚀
This helps to prioritize the content which you are interested in. The implementation contains scenes for ChatGPT
requests, Strava-Stats and some other random content generating scenes.

## Current Scenes
* ChatGPTScene
* SnapshotScene
* StravaLastActivityScene
* WasteCalendarScene
"""

app = FastAPI(
    title="vestaboard-control",
    description=description)


# FastAPI Logging anpassen
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(logging_config)

logger = setup_custom_logger(__file__)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        if ConfigHelper.get_vboard_read_write_key() is None:
            return JSONResponse(
                content={
                    "message": "Missing your Vestaboard API key. Please create a settings.ini file within the /config directory"},
                status_code=400
            )

        response = await call_next(request)
        return response

    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        logger.exception(e)

        return JSONResponse(
            content={"message": "Internal Server Error"},
            status_code=500
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(strava.router)
app.include_router(developer.router)
app.include_router(lifecycle.router)
app.include_router(snapshots.router)
app.include_router(execute.router)
app.include_router(frontend.router)


