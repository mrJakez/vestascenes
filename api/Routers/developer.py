import vesta
from fastapi import APIRouter
from starlette.responses import RedirectResponse

import Scenes.BirthdayScene
from Helper.ConfigHelper import ConfigHelper
from Helper.RawHelper import RawHelper
from Scenes import *
import importlib

import subprocess
from vesta.chars import Rows
from vesta.vbml import Component

router = APIRouter()
vboard = vesta.ReadWriteClient("3e5dc670+a418+43f0+acd5+4ff8cc5fb2fd")

@router.get("/", tags=["developer support"])
async def root_path():
    return RedirectResponse("/status")

@router.get("/test-scene/{scene_class_sring}/{send_to_board}", tags=["developer support"])
async def test_scene(scene_class_sring: str = None, send_to_board: bool = False):


    print(f"send_to_board {send_to_board}")

    if scene_class_sring is None:
        return {"message": "please define a scene class name which you want to test"}

    MyClass = getattr(importlib.import_module(f"Scenes.{scene_class_sring}"), scene_class_sring)
    scene = MyClass()
    scene.post_execution = True
    res = scene.execute()

    if res.raw is not None:
        vesta.pprint(res.raw)
        if send_to_board:
            try:
                vboard.write_message(res.raw)
            except Exception as exc:
                print(f"HTTP Exception catched")

    return {"message": res.message}


@router.get("/priorities", tags=["developer support"])
async def priorities():
    return Scenes.Director().get_priorities()


@router.get("/status", tags=["developer support"])
async def priorities():
    gitHash = '-'
    try:
        gitHash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    except Exception as e:
        print(f"error {e}")

    return {
        "enabled": f"{(not ConfigHelper.is_disabled())}",
        "git-hash": gitHash,
        "strava-initialized": f"{Scenes.StravaLastActivityScene.StravaLastActivityScene.is_initialized()}",
        "version-check" : "3"
    }
