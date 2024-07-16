import os

from fastapi import APIRouter
from sqlmodel import Session, delete

from Helper.ConfigHelper import ConfigHelper
from Models.SceneInstanceModel import SceneInstanceModel
from Models.SnapshotModel import SnapshotModel
from Repository import Repository

router = APIRouter()

@router.get("/init/", tags=["lifecycle"], description="Initilaizes the vestaboard config and database")
async def init():
    if os.path.exists("/database/vbcontrol.db"):
        print("old database existed - removed right now")
        os.remove("/database/vbcontrol.db")

    if os.path.exists("strava.ini"):
        print("old strava config existed - removed right now")
        os.remove("strava.ini")

    Repository()._engine = None
    Repository().create_tables()

    await init_snapshots()
    return {"status": "initalization done successfully"}

@router.get("/init-snapshots/", tags=["lifecycle"], description="Adds all snapshots which are stored within the Initial-Snapshots/ folder into the database")
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

    return {"status": f"added {addedScreenshotsCount} snapshots"}


@router.get("/reset-instances/", tags=["lifecycle"])
async def reset_instances():
    with Session(Repository().get_engine()) as session:
        statement = delete(SceneInstanceModel)
        result = session.exec(statement)
        session.commit()
    return {"message": "scene_instances cleared successfully"}



@router.get("/disable/{status}", tags=["lifecycle"])
async def enable_status(status):
    ConfigHelper.set_disabled(status)
    return {"message": f"set to {status}"}