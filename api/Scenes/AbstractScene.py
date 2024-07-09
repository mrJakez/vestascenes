import datetime
import string
import uuid
from enum import Enum

import vesta


# SceneType specifies if the scene is something which is time relative or just a "random" artwork
class SceneType(Enum):
    # Artwork Scenes are "filling scenes" to provide some nice content which is not in relation to any time event
    ARTWORK = 1
    # timed scenes are scenes which are just relevant for a specific time. Like strava last activity, waste calendar etc.
    TIMED = 2


class SceneExecuteReturn:
    def __init__(self, id, should_execute, priority, scene_object, start_date = None, end_date = None, message = None, raw = None):
        self.id = id
        self.should_execute = should_execute
        self.priority = priority
        self.scene_object = scene_object
        self.start_date = start_date
        self.end_date = end_date
        self.message = message
        self.raw = raw


    # a unique ID which is used to identify if the content of this scene instance was already displayed.
    id: string

    # a scene can also specify if it has content or not
    should_execute: bool
    priority: int
    scene_object: object

    # a message which is mainly used for debug reasons.
    message: string

    start_date: datetime
    end_date: datetime

    # the raw content of a scene. If should_execute=True the raw content is mandatory => it will be displayed towards
    # vestaboard when the director identifies the current scene instance as best next scene
    raw: list


class AbstractScene:

    type: SceneType = SceneType.ARTWORK

    # default priority. Steers the order of scenes
    priority: int = 100

    def execute(self) -> SceneExecuteReturn:
        raise Exception(f"Sorry, execute() not implemented within class {self.__class__.__name__}")

    # invented to save money for the chatgpt execution. Thanks to this the chatgpt scene (when choosen as candidate)
    # will NOT be triggered if this will not be displayed.
    def post_execute(self) -> SceneExecuteReturn:
        return None


class DemoScene(AbstractScene):
    def execute(self, vboard):
        message = "Hello, World"
        raw = vesta.encode_text(message)
        start_date = datetime.now()
        end_date = start_date + datetime.timedelta(minutes=1)
        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self, start_date, end_date, message, raw)

