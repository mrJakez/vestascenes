from datetime import datetime

import vesta
from fastapi import APIRouter

from Helper.ConfigHelper import ConfigHelper
from Models.SceneInstanceModel import SceneInstanceModel
from Repository import Repository
from Scenes.AbstractScene import SceneExecuteReturn
from Scenes.Director import Director

router = APIRouter()
vboard = vesta.ReadWriteClient("3e5dc670+a418+43f0+acd5+4ff8cc5fb2fd")


@router.get("/execute", tags=["main"],
            description="This service is the real worker process. It determines the next candidate and"
                        "validates the current state. If a higher priority is given by the candidate scene the vestabaord "
                        "will be updated. Gets executed all 15 min. by dedicated runner container.")
async def execute():
    if ConfigHelper.is_disabled() is True:
        return {"message": "disabled"}

    now = datetime.now()

    operation_hour_error = ConfigHelper.is_in_operation_hours(now)
    if operation_hour_error is not None:
        return operation_hour_error

    candidate: SceneExecuteReturn = Director(vboard).get_next_scene()
    print(f"candidate: {candidate.scene_object.__class__.__name__} (ID: {candidate.id})")
    current = Repository().get_active_scene_instance()

    # debug
    if current is not None:
        end_date = datetime.strptime(current.end_date, "%Y-%m-%d %H:%M:%S.%f")
        print(f"now: {now} - end date: {end_date} (Difference: {(end_date - now).total_seconds()})")
    # -

    if current is None:
        print("current is none -> candidate will be executed")
    elif datetime.strptime(current.end_date, "%Y-%m-%d %H:%M:%S.%f") >= now:
        print(f"current ({current.class_string}) is still valid (end_date not reached yet)")
        if candidate.priority > current.priority:
            print("candidate has higher priority than current. Current will be replaced")
            Repository().unmark_active_scene_instance()
        else:
            # noinspection PyUnboundLocalVariable
            return {
                "identifier": current.id,
                "scene": current.class_string,
                "message": f"candidate has lower or equal priority than current -> keep current (seconds left:{int((end_date - now).total_seconds())})",
                "end_date": end_date
            }

    elif datetime.strptime(current.end_date, "%Y-%m-%d %H:%M:%S.%f") < now:
        print("current is not valid any longer - is_active will be set to false")
        Repository().unmark_active_scene_instance()

    post_execution_candidate = candidate.scene_object.post_execute(vboard)
    if post_execution_candidate is not None:
        print("-----------------------------------------> execute post execution candidate!")
        candidate = post_execution_candidate

    print(f"candidate.message: {candidate.message} - {candidate.raw}")
    vesta.pprint(candidate.raw)

    try:
        vboard.write_message(candidate.raw)
        # print("lala")
    except TypeError as exc:
        print(f"HTTP Exception catched {exc}")

    model = SceneInstanceModel(scene=candidate)
    Repository().save_scene_instance(model)

    return {
        "identifier": candidate.id,
        "scene": candidate.scene_object.__class__.__name__,
        "message": candidate.message,
        "start_date": candidate.start_date,
        "end_date": candidate.end_date
    }
