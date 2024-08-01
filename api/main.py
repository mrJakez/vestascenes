import sys
import os
import time
from fastapi import FastAPI

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


app.include_router(strava.router)
app.include_router(developer.router)
app.include_router(lifecycle.router)
app.include_router(snapshots.router)
app.include_router(execute.router)


