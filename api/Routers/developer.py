import vesta
from fastapi import APIRouter

from Helper.ConfigHelper import ConfigHelper
from Helper.RawHelper import RawHelper
from Scenes.Director import Director
from Scenes.StravaLastActivityScene import StravaLastActivityScene
from Scenes.WasteCalendarScene import WasteCalendarScene
from Scenes.ChatGPTScene import ChatGPTScene

import subprocess
from vesta.chars import Rows
from vesta.vbml import Component


router = APIRouter()


@router.get("/test-scene", tags=["developer support"])
async def test_scene():
    #scene = SnapshotScene()
    #scene = StravaLastActivityScene()
    #scene = ChatGPTScene()
    scene = WasteCalendarScene()
    scene.post_execution = True
    res = scene.execute()

    if res.raw is not None:
        vesta.pprint(res.raw)

    return {"message": res.message}


@router.get("/priorities", tags=["developer support"])
async def priorities():
    return Director().get_priorities()


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
        "strava-initialized": f"{StravaLastActivityScene.is_initialized()}",
        "version-check" : "2"
    }
