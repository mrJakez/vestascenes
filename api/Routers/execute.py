from datetime import datetime

import vesta
from fastapi import APIRouter
from httpx import HTTPStatusError

from Helper.ConfigHelper import ConfigHelper
from Helper.VboardHelper import VboardHelper
from Models.SceneInstanceModel import SceneInstanceModel
from Repository import Repository
from Scenes.AbstractScene import SceneExecuteReturn
from Scenes.Director import Director

router = APIRouter()
vboard = VboardHelper().get_client()


@router.get("/execute", tags=["main"],
            description="This service is the real worker process. It determines the next candidate and"
                        "validates the current state. If a higher priority is given by the candidate scene the vestabaord "
                        "will be updated. Gets executed all 15 min. by dedicated runner container.")
async def execute(ignore_operation_hour:bool = False):
    if ConfigHelper.is_disabled() is True:
        return {"message": "disabled"}

    now = datetime.now()

    operation_hour_error = ConfigHelper.is_in_operation_hours(now)
    if ignore_operation_hour is False and operation_hour_error is not None:
        return operation_hour_error

    candidate: SceneExecuteReturn = Director(vboard).get_next_scene()
    print(f"candidate: {candidate.scene_object.__class__.__name__} (ID: {candidate.id})")
    current = Repository().get_active_scene_instance()

    # debug
    if current is not None:
        end_date = current.get_end_date()
        print(f"now: {now} - end date: {end_date} (Difference: {(end_date - now).total_seconds()})")
    # -

    if current is None:
        print("current is none -> candidate will be executed")
    elif current.get_end_date() >= now:
        print(f"current ({current.class_string}) is still valid (end_date not reached yet)")
        if candidate.priority > current.priority:
            print("candidate has higher priority than current. Current will be replaced")
            Repository().unmark_active_scene_instance()
        else:
            # noinspection PyUnboundLocalVariable
            return {
                "current": {
                    "identifier": current.id,
                    "scene": current.class_string,
                },
                "candidate": {
                    "class": candidate.scene_object.__class__.__name__,
                    "message": candidate.message
                },
                "message": f"candidate has lower or equal priority than current -> keep current (seconds left:{int((end_date - now).total_seconds())})",
                "end_date": end_date
            }

    elif current.get_end_date() < now:

        suppressed_scene_instance = Repository().get_suppressed_scene_instance()
        print("current is not valid any longer - is_active will be set to false")
        Repository().unmark_active_scene_instance()

        # check if there is an old entry in the scene instances which is still valid but which was overruled by something with a higher priority.

        if suppressed_scene_instance is not None:
            Repository().mark_scene_instance_as_active(suppressed_scene_instance)
            await vboard_print(suppressed_scene_instance.get_raw_list())
            print("restore existing scene instance!")
            return {
                "identifier": suppressed_scene_instance.id,
                "scene": suppressed_scene_instance.class_string,
                "message": "replaced existing candidate",
                "start_date": suppressed_scene_instance.start_date,
                "end_date": suppressed_scene_instance.end_date
            }



    post_execution_candidate = candidate.scene_object.post_execute(vboard)
    if post_execution_candidate is not None:
        print("-----------------------------------------> execute post execution candidate!")
        candidate = post_execution_candidate

    print(f"candidate.message: {candidate.message} - {candidate.raw}")
    vesta.pprint(candidate.raw)

    await vboard_print(candidate.raw)

    model = SceneInstanceModel(scene=candidate)
    Repository().save_scene_instance(model)

    return {
        "identifier": candidate.id,
        "scene": candidate.scene_object.__class__.__name__,
        "message": candidate.message,
        "start_date": candidate.start_date,
        "end_date": candidate.end_date
    }


async def vboard_print(raw: list):
    try:
        vboard.write_message(raw)
        # print("lala")
    except TypeError as exc:
        print(f"HTTP Exception catched {exc}")
    except HTTPStatusError as exc:
        if exc.response.status_code == 304:
            print("Exception: currently displayed message is the same than new one")
