import vesta
from fastapi import APIRouter

from Scenes.Director import Director
from Scenes.StravaLastActivityScene import StravaLastActivityScene

import subprocess

# from fastapi import FastAPI, Request

router = APIRouter()


@router.get("/test-scene", tags=["developer support"])
async def test_scene():
    #scene = SnapshotScene()
    scene = StravaLastActivityScene()
    #scene = WasteCalendarScene()
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
    except subprocess.CalledProcessError as e:
        print(f"error {e}")

    return {
        "git-hash": gitHash,
        "strava-initialized": f"{StravaLastActivityScene.is_initialized()}"
    }
