import configparser
from datetime import datetime, timedelta
import string
import uuid
from enum import Enum
from typing import Optional, Dict

import vesta

from Helper.ConfigHelper import ConfigHelper, get_config

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)

# SceneType specifies if the scene is something which is time relative or just a "random" artwork
class SceneType(Enum):
    # Artwork Scenes are "filling scenes" to provide some nice content which is not in relation to any time event
    ARTWORK = 1
    # timed scenes are scenes which are just relevant for specific time. Like strava last activity, waste calendar etc.
    TIMED = 2


class SceneExecuteReturn:
    def __init__(self, unique_id, should_execute, priority, scene_object, start_date=None, end_date=None, message=None,
                 raw=None):
        self.id = unique_id
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

    @classmethod
    def error(cls, scene: object, message: string):
        res = SceneExecuteReturn(f"error_{str(uuid.uuid4())}", False, 0, scene_object=scene, message=message)
        logger.debug(f"scene: {scene.__class__.__name__} message: {message}")
        return res


class AbstractScene:
    type: SceneType = SceneType.ARTWORK

    # default priority. Steers the order of scenes
    priority: int = 100

    # used for artwork scenes. With the weight property specific artwork scenes can dominate others.
    weight: int = 1

    # used for some frontend cases. In previews I would like to render some content anyways
    force_positive_rendering: bool = False

    # some scenes may collect new content during their run. For example the strava scene -> when the title is updated or
    # a clock scene. In these cases the scene can be flagged as overwritable -> which does mean the new content of the
    # new run will be taken and will replace the existing one. Please remember that the uniqueId of the corresponding
    # SceneExecuteReturn object also needs to be updated/changed. Otherwise the scene will not be refreshed.
    overwritable: bool = False

    # The previous_identifier was optionally introduced that a scene which has an overwritable feature has a chance to
    # react on the configuration of the initial scene. This requires a well defined identifier which helps to provide
    # all required information towards the overwritable execute() call. This currently just works for artwork scenes!

    # This was introduced on behalve of the countdown scene, as the updates should take into account the current
    # countdown item.
    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        raise Exception(f"Sorry, execute() not implemented within class {self.__class__.__name__}")

    # invented to save money for the chatgpt execution. Thanks to this the chatgpt scene (when chosen as candidate)
    # will NOT be triggered if this will not be displayed.
    def post_execute(self, vboard) -> Optional[SceneExecuteReturn]:
        return None

    # noinspection PyMethodMayBeStatic
    def get_next_full_hour(self) -> datetime:
        start_date = datetime.now()
        end_date = start_date + timedelta(minutes=60)
        end_date = end_date.replace(minute=0, second=0, microsecond=1)
        return end_date

    def get_config(self, key: str = None):
        config = configparser.ConfigParser()
        config.read(['/config/settings.ini'])

        if config.has_section(self.__class__.__name__) is False:
            if key is None:
                return {}
            else:
                return None

        if key is None:
            return config[self.__class__.__name__]
        elif key in config[self.__class__.__name__]:
            return config[self.__class__.__name__][key]
        else:
            return None

    def save_config(self, new_config: Dict[str, str]):
        config = configparser.ConfigParser()
        config.read(['/config/settings.ini'])

        if config.has_section(self.__class__.__name__) is False:
            config.add_section(self.__class__.__name__)

        old = dict(config.items(self.__class__.__name__))
        merged = old | new_config

        config[self.__class__.__name__] = merged

        with open('/config/settings.ini', 'w') as configfile:
            config.write(configfile)
