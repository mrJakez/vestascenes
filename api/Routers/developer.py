import vesta
from fastapi import APIRouter
from starlette.responses import RedirectResponse
from pathlib import Path

import Scenes.BirthdayScene
import Scenes.StravaLastActivityScene
from Models.SceneInstanceModel import SceneInstanceModel
from Scenes.Director import Director
from Helper.ConfigHelper import ConfigHelper
from Helper.RawHelper import RawHelper
from Helper.VboardHelper import VboardHelper
from Helper.Logger import setup_custom_logger

import importlib

from Repository import Repository

router = APIRouter()
vboard = VboardHelper().get_client()

logger = setup_custom_logger(__file__)


@router.get("/", tags=["developer support"])
async def root_path():
    return RedirectResponse("/status")


@router.get("/test-scene/{scene_class_string}/{send_to_board}", tags=["developer support"])
async def test_scene(scene_class_string: str = None, send_to_board: bool = False):
    logger.info(f"send_to_board: {send_to_board}")

    if scene_class_string is None:
        return {"message": "please define a scene class name which you want to test"}

    director = Director(vboard)
    scene = director.get_scene(scene_class_string)
    scene.post_execution = True

    res = scene.execute(vboard)

    if res.raw is not None:
        vesta.pprint(res.raw)
        if send_to_board:
            try:
                Repository().unmark_active_scene_instance()
                model = SceneInstanceModel(scene_exec_return=res)
                Repository().save_scene_instance(model)

                vboard.write_message(res.raw)
            except Exception as exc:
                logger.error(f"HTTP Exception catched {exc}")

    logger.info(f"/test-scene executed:{res.message}")

    return {
        "should_execute": res.should_execute,
        "message": res.message,
        "start_date": res.start_date,
        "end_date": res.end_date,
        "priority": res.priority
    }


@router.get("/priorities", tags=["developer support"])
async def priorities():
    return Scenes.Director.Director(vboard).get_priorities()


@router.get("/status", tags=["developer support"])
async def status():
    vboard_initialized = False
    if VboardHelper().get_client() is not None:
        vboard_initialized = True

    return {
        "version-check": 18,
        "enabled": (not ConfigHelper.is_disabled()),
        "git-hash": ConfigHelper.get_git_hash(),
        "strava-initialized": Scenes.StravaLastActivityScene.StravaLastActivityScene.is_initialized(),
        "vboard-initialized": vboard_initialized
    }


@router.get("/read-current", tags=["developer support"])
async def read_current():
    client = VboardHelper().get_client()
    raws = client.read_message()

    return {
        "raw": RawHelper.get_raw_string(raws)
    }