import sys
# this is required to work within the docker container
sys.path.append('/app/api/')

import os, time
from fastapi import FastAPI, Request
import vesta
from datetime import datetime
import configparser

from Repository import Repository
from stravalib import Client

from Scenes.Director import Director
from Scenes.AbstractScene import AbstractScene
from Scenes.StravaLastActivityScene import StravaLastActivityScene
from Scenes.WasteCalendarScene import WasteCalendarScene
from Scenes.SnapshotScene import SnapshotScene


from Helper.ConfigHelper import ConfigHelper

from Models.SnapshotModel import SnapshotModel
from Models.SceneInstanceModel import SceneInstanceModel
from fastapi.encoders import jsonable_encoder

from sqlmodel import Session, delete
import json
from pprint import pprint

os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

description = """
This is a vestaboard server implementation which organizes the vestaboard related content within scenes. 🚀
This helps to priotize the content which you are interested in. The implementation contans scenes for ChatGPT
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
vboard = vesta.ReadWriteClient("3e5dc670+a418+43f0+acd5+4ff8cc5fb2fd")


@app.get("/execute", tags=["main"],
         description="This service is the real worker process. It determines the next candidate and"
                     "validates the current state. If a higher priority is given by the candidate scene the vestabaord "
                     "will be updated. Gets executed all 15 min. by dedicated runner container.")
async def execute():
    if ConfigHelper.is_disabled() is True:
        return {"message" : "disabled"}

    now = datetime.now()

    operation_hour_error = ConfigHelper.is_in_operation_hours(now)
    if not operation_hour_error is None:
        return operation_hour_error

    candidate:AbstractScene = Director().get_next_scene()
    print(f"candidate: {candidate.scene_object.__class__.__name__} (ID: {candidate.id})")
    current = Repository().get_active_scene_instance()

    # debug
    if current is not None:
        end_date = datetime.strptime(current.end_date, "%Y-%m-%d %H:%M:%S.%f")
        print(f"now: {now} - end date: {end_date} (Difference: {(end_date - now).total_seconds()})")
    #-

    if current is None:
        print("current is none -> candidate will be executed")
    elif datetime.strptime(current.end_date, "%Y-%m-%d %H:%M:%S.%f") >= now:
        print(f"current ({current.class_string}) is still valid (end_date not reached yet)")
        if candidate.priority > current.priority:
            print("candidate has higher priority than current. Current will be replaced")
            Repository().unmark_active_scene_instance()
        else:
            return {
                "identifier": current.id,
                "scene": current.class_string,
                "message": f"candidate has lower or equal priority than current -> keep current (seconds left:{int((end_date - now).total_seconds())})",
                "end_date": end_date
            }

    elif datetime.strptime(current.end_date, "%Y-%m-%d %H:%M:%S.%f") < now:
        print("current is not valid any longer - is_active will be set to false")
        Repository().unmark_active_scene_instance()

    post_execution_candidate = candidate.scene_object.post_execute()
    if post_execution_candidate is not None:
        print("-----------------------------------------> execute post execution candidate!")
        candidate = post_execution_candidate

    print(f"candidate.message: {candidate.message} - {candidate.raw}")
    vesta.pprint(candidate.raw)

    try:
        vboard.write_message(candidate.raw)
        #print("lala")
    except Exception as exc:
        print(f"HTTP Exception catched")

    model = SceneInstanceModel(scene=candidate)
    Repository().save_scene_instance(model)

    return {
        "identifier": candidate.id,
        "scene": candidate.scene_object.__class__.__name__,
        "message": candidate.message,
        "start_date": candidate.start_date,
        "end_date": candidate.end_date
    }


# /storeSnapshot is storing the current vestaboard message within the snappshots database table
@app.get("/storeSnapshot/{title}", tags=["main"])
async def store_snapshot(title: str):
    current_message = vboard.read_message()
    current_message_string = str(current_message).replace(' ', '')

    print("current_message:")
    vesta.pprint(current_message)

    snapshot = SnapshotModel(title=title, raw=current_message_string)
    json_snapshot = jsonable_encoder(snapshot)
    Repository().store_snapshot(snapshot)

    return {
        "status": "created",
        "snapshot": json_snapshot
    }


@app.get("/snapshots", tags=["main"])
async def snapshots():
    return {"snapshots": Repository().get_snapshots()}


@app.get("/authorize-strava", tags=["strava-oauth"], description="Initilaizes the strava connection. Returns an "
                                                                 "authorization link which will trigger the callback url afterwards.")
async def authorize_strava(request: Request):
    client = Client()
    url = client.authorization_url(client_id=StravaLastActivityScene.client_id,
                                   redirect_uri=f"http://{request.url.hostname}:{request.url.port}/authorize-strava-callback")

    return {"initialized": f"{StravaLastActivityScene.is_initialized()}", "url": url}


@app.get("/authorize-strava-callback", tags=["strava-oauth"], description="Callback which is triggered by the "
                                                                          "strava authorization process. Within a success case the access and refresh tokens are provided and stored in a local configuration.")
async def authorize_strava_callback(code: str):
    client = Client()

    token_response = client.exchange_code_for_token(client_id=StravaLastActivityScene.client_id,
                                                    client_secret=StravaLastActivityScene.client_secret,
                                                    code=code)

    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']  # You'll need this in 6 hours
    expires_at = token_response['expires_at']

    StravaLastActivityScene.store_tokens(access_token, refresh_token, expires_at)
    return {"status": f"access_token: {access_token} refresh_token: {refresh_token} expires_at: {expires_at}"}


@app.get("/init/", tags=["developer support"], description="Initilaizes the vestaboard config and database")
async def init():
    if os.path.exists("/database/vbcontrol.db"):
        print("old database existed - removed right now")
        os.remove("/database/vbcontrol.db")

    Repository()._engine = None
    Repository().create_tables()

    init_snapshots()
    return {"status": "initalization done successfully"}

@app.get("/init-snapshots/", tags=["developer support"], description="Adds all snapshots which are stored within the Initial-Snapshots/ folder into the database")
async def init_snapshots():
    directory = os.fsencode("Initial-snapshots/")
    addedScreenshotsCount = 0


    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        print(filename)
        if filename.endswith(".raw"):
            file = open(f"Initial-snapshots/{filename}", 'r')
            lines = file.readlines()

            for line in lines:
                if len(line) < 2:
                    continue

                title = filename.replace(".raw", "")

                if "#" in line:
                    title += " - " + line.split("#")[0]
                    raw = line.split("#")[1]
                else:
                    raw = line

                snapshot = SnapshotModel(title=title, raw=raw)
                if Repository().store_snapshot(snapshot) == True:
                    addedScreenshotsCount += 1

                print(f"title: {title}, raw: {raw}")

    return {"status": f"added {addedScreenshotsCount} snapshots", "foo":"bar"}



@app.get("/reset-instances", tags=["developer support"])
async def reset_instances():
    with Session(Repository().get_engine()) as session:
        statement = delete(SceneInstanceModel)
        result = session.exec(statement)
        session.commit()
    return {"message": "scene_instances cleared successfully"}


@app.get("/test-scene", tags=["developer support"])
async def test_scene():
    scene = SnapshotScene()
    #scene = StravaLastActivityScene()
    #scene = WasteCalendarScene()
    scene.post_execution = True
    res = scene.execute()

    if res.raw is not None:
        vesta.pprint(res.raw)

    return {"message": res.message}


@app.get("/priorities", tags=["developer support"])
async def priorities():
    return Director().get_priorities()


@app.get("/disable/{status}", tags=["developer support"])
async def enable_status(status):
    ConfigHelper.set_disabled(status)
    return {"message": f"set to {status}"}
