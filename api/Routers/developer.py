import vesta
from fastapi import APIRouter
from starlette.responses import RedirectResponse

import Scenes.BirthdayScene
import Scenes.StravaLastActivityScene
import Scenes.Director
from Helper.ConfigHelper import ConfigHelper
from Helper.VboardHelper import VboardHelper
import importlib

import subprocess

router = APIRouter()
vboard = VboardHelper().get_client()


@router.get("/", tags=["developer support"])
async def root_path():
    return RedirectResponse("/status")


@router.get("/test-scene/{scene_class_string}/{send_to_board}", tags=["developer support"])
async def test_scene(scene_class_string: str = None, send_to_board: bool = False):
    print(f"send_to_board {send_to_board}")

    if scene_class_string is None:
        return {"message": "please define a scene class name which you want to test"}

    my_class = getattr(importlib.import_module(f"Scenes.{scene_class_string}"), scene_class_string)
    scene = my_class()
    scene.post_execution = True
    res = scene.execute(vboard)

    if res.raw is not None:
        vesta.pprint(res.raw)
        if send_to_board:
            try:
                vboard.write_message(res.raw)
            except Exception as exc:
                print(f"HTTP Exception catched {exc}")

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
async def priorities():
    git_hash = '-'
    try:
        git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    except Exception as e:
        print(f"error {e}")

    vboard_initialized = False
    if VboardHelper().get_client() is not None:
        vboard_initialized = True

    return {
        "version-check": 15,
        "enabled": (not ConfigHelper.is_disabled()),
        "git-hash": git_hash,
        "strava-initialized": Scenes.StravaLastActivityScene.StravaLastActivityScene.is_initialized(),
        "vboard-initialized": vboard_initialized
    }
