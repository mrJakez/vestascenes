from datetime import datetime
from typing import Union

import vesta
from fastapi import APIRouter
from httpx import HTTPStatusError

from Helper.ConfigHelper import ConfigHelper
from Helper.VboardHelper import VboardHelper
from Helper.RawHelper import RawHelper
from Models.SceneInstanceModel import SceneInstanceModel
from Repository import Repository
from Scenes.AbstractScene import SceneExecuteReturn
from Scenes.Director import Director
from Helper.Logger import setup_custom_logger
from itertools import islice
from pydantic import BaseModel
from typing import List

from Scenes.TextScene import TextScene

router = APIRouter()
vboard = VboardHelper().get_client()

logger = setup_custom_logger(__file__)

@router.get("/frontend/scenes", tags=["frontend support"])
async def scenes():
    return {
        "meta": {},
        "content": Director(vboard).get_priorities()
    }


@router.get("/frontend/scene/{scene_class_string}", tags=["frontend support"])
async def test_scene(scene_class_string: str = None):
    if scene_class_string is None:
        return {"message": "please define a scene class name which you want to test"}

    director = Director(vboard)
    scene = director.get_scene(scene_class_string)
    scene.force_positive_rendering = True
    scene.post_execution = True
    res = scene.execute(vboard)

    logger.info(f"/frontend/scene/test-scene executed:{res.message}")

    return {
        "should_execute": res.should_execute,
        "message": res.message,
        "start_date": res.start_date,
        "end_date": res.end_date,
        "priority": res.priority,
        "raw": res.raw,
    }

@router.get("/frontend/snapshot-filenames/", tags=["frontend support"])
async def snapshot_filenames():

    snapshots = Repository().get_snapshots()
    filenames: [str] = []
    for snapshot in snapshots:
        if snapshot.get_filename() not in filenames:
            filenames.append(snapshot.get_filename())

    return {
        "meta": {},
        "content": filenames
    }


@router.get("/frontend/snapshots/", tags=["frontend support"])
async def snapshots(filename: Union[str, None] = None):
    return {
        "meta": {},
        "content": Repository().get_snapshots(filename=filename)
    }





@router.get("/frontend/history", tags=["frontend support"])
async def history():
    logger.info(f"frontend -> get history")

    res = []
    for instance in islice(Repository().get_scene_instances(), 50):
        res.append(instance.model_dump())

    return {
        "meta": {},
        "content": res
    }


class BoardWriteRequest(BaseModel):
    mode: str
    boardValue: List

@router.post("/frontend/write", tags=["frontend support"])
async def write(request: BoardWriteRequest):
    logger.info(f"frontend -> write")
    mode = request.mode

    director = Director(vboard)
    scene = TextScene()
    scene.raw = request.boardValue

    res = scene.execute(vboard)
    VboardHelper().print(res)

    return {
        "meta": {},
        "content": f"{res.message}",
        "mode": f"{mode}"
    }