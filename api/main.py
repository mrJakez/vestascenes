import sys
import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from Helper.ConfigHelper import ConfigHelper

# this is required to work within the docker container
sys.path.append('/app/api/')

# noinspection PyPep8
from Routers import strava, developer, lifecycle, snapshots, execute

os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if ConfigHelper.get_vboard_read_write_key() is None:
        return JSONResponse(content={"message": "Missing your vestaboard API key. Please create a settings.ini file within the /config directory"})
    else:
        response = await call_next(request)
        return response


app.include_router(strava.router)
app.include_router(developer.router)
app.include_router(lifecycle.router)
app.include_router(snapshots.router)
app.include_router(execute.router)


