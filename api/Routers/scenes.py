import logging

import vesta
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from Helper.Logger import setup_custom_logger
from Models.SnapshotModel import SnapshotModel
from Repository import Repository
from Helper.VboardHelper import VboardHelper
from Scenes.Director import Director
from Scenes.TimerScene import TimerScene
from Scenes.TextScene import TextScene

from pydantic import BaseModel
from typing import List
router = APIRouter()
vboard = VboardHelper().get_client()

logger = setup_custom_logger(__file__)

class BoardWriteRequest(BaseModel):
    mode: str
    boardValue: List

@router.post("/text", tags=["scenes"])
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

@router.post("/timer", tags=["scenes"])
async def create_timer(payload: dict = Body(...)):
    """
    Payload Beispiel: {'id': 'timer_1', 'title': 'Staubsauger Timer', 'run_duration_seconds': 300}
    """
    logger.info(f"timer -> create {dict(payload)}")


    director = Director(vboard)
    scene = TimerScene()
    scene.timer_id = payload["id"]
    scene.title = payload["title"]
    scene.run_duration_seconds = payload["run_duration_seconds"]

    res = scene.execute(vboard)
    VboardHelper().print(res)

    return {
        "meta": {},
        "content": f"{res.message}",
    }

@router.get("/delete-timer/{timerid}", tags=["scenes"])
async def delete_timer(timerid):
    scene = Repository().get_active_scene_instance()
    if scene is not None and scene.class_string == 'TimerScene':
        if scene.id.startswith(f"Timer_{timerid}_"):
            Repository().unmark_active_scene_instance()
            return {"message": f"deleted {timerid}"}

    return {"message": f"No current TimerScene with ID {timerid} found."}