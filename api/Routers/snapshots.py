import logging

import vesta
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from Models.SnapshotModel import SnapshotModel
from Repository import Repository
from Helper.VboardHelper import VboardHelper

router = APIRouter()
vboard = VboardHelper().get_client()


# /storeSnapshot is storing the current vestaboard message within the snapshots database table
@router.get("/storeSnapshot/{title}", tags=["snapshots"])
async def store_snapshot(title: str):
    current_message = vboard.read_message()
    current_message_string = str(current_message).replace(' ', '')

    logging.info("current_message:")
    vesta.pprint(current_message)

    snapshot = SnapshotModel(title=title, raw=current_message_string)
    json_snapshot = jsonable_encoder(snapshot)
    Repository().store_snapshot(snapshot)

    return {
        "status": "created",
        "snapshot": json_snapshot
    }


@router.get("/snapshots", tags=["snapshots"])
async def snapshots():
    return {"snapshots": Repository().get_snapshots()}
