import os
import json
import time

from fastapi import APIRouter, Request
from fastapi.testclient import TestClient

from sqlmodel import Session, delete

from Helper.ConfigHelper import ConfigHelper
from Models.SceneInstanceModel import SceneInstanceModel
from Models.SnapshotModel import SnapshotModel
from Repository import Repository

router = APIRouter()


@router.get("/init/", tags=["lifecycle"], description="Initializes the vestaboard config and database")
async def init():
    if os.path.exists("/database/vbcontrol.db"):
        print("old database existed - removed right now")
        os.remove("/database/vbcontrol.db")

    if os.path.exists("/config/strava.ini"):
        print("old strava config existed - removed right now")
        os.remove("/config/strava.ini")

    Repository()._engine = None
    Repository().create_tables()

    await init_snapshots()
    return {"status": "initialization done successfully"}


@router.get("/init-snapshots/", tags=["lifecycle"],
            description="Adds all snapshots which are stored within the Initial-Snapshots/ folder into the database")
async def init_snapshots():
    directory = os.fsencode("Initial-snapshots/")
    added_screenshots_count = 0

    start_time = time.time()

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        print(f"file.{filename}: {time.time() - start_time}")

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
                if Repository().store_snapshot(snapshot):
                    print(f"snapshot {title} addded: {time.time() - start_time}")
                    added_screenshots_count += 1

    print(f"total time: {time.time() - start_time}")
    return {"status": f"added {added_screenshots_count} snapshots"}


@router.get("/reset-instances/", tags=["lifecycle"])
async def reset_instances():
    with Session(Repository().get_engine()) as session:
        statement = delete(SceneInstanceModel)
        session.exec(statement)
        session.commit()
    return {"message": "scene_instances cleared successfully"}


@router.get("/disable/{status}", tags=["lifecycle"])
async def enable_status(status):
    ConfigHelper.set_disabled(status)
    return {"message": f"set to {status}"}


@router.get("/refresh", tags=["lifecycle"])
async def refresh(request: Request):
    Repository().unmark_active_scene_instance()

    client = TestClient(request.app)
    response = client.get("/execute?ignore_operation_hour=true")
    return json.loads(response.text)
