import random
from datetime import datetime
from typing import List

from vesta import ReadWriteClient

from Scenes.AbstractScene import AbstractScene, SceneType, SceneExecuteReturn
from Scenes.BirthdayScene import BirthdayScene
from Scenes.ChatGPTScene import ChatGPTScene
from Scenes.NewReleaseScene import NewReleaseScene
from Scenes.SnapshotScene import SnapshotScene
from Scenes.StravaLastActivityScene import StravaLastActivityScene
from Scenes.WasteCalendarScene import WasteCalendarScene
from Scenes.ClockScene import ClockScene
from Repository import Repository

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)

class Director:
    vboard: ReadWriteClient

    def __init__(self, vboard: ReadWriteClient):
        self.vboard = vboard

    def get_next_scene(self) -> SceneExecuteReturn:

        returns = []
        for timed_scene in self.__all_scenes(SceneType.TIMED):
            execute_res = timed_scene.execute(self.vboard)

            if execute_res.should_execute is not True:
                continue

            if Repository().scene_instances_with_id_exists(execute_res.id):
                continue

            if execute_res.start_date > datetime.now():
                continue

            returns.append(execute_res)

        # order SceneExecuteReturn objects based on priority
        returns.sort(key=lambda x: x.priority, reverse=True)

        if len(returns) > 0:
            logger.info("Found a TIMED scene")
            return returns[0]
        else:
            artwork_scene = random.choice(self.__all_scenes(SceneType.ARTWORK, weighted=True))
            return artwork_scene.execute(self.vboard)

    # noinspection PyMethodMayBeStatic
    def __all_scenes(self, scene_type=None, weighted=False) -> List[AbstractScene]:

        scenes = []  # empty array

        if scene_type is None or scene_type is SceneType.TIMED:
            scenes.append(NewReleaseScene())
            scenes.append(WasteCalendarScene())
            scenes.append(StravaLastActivityScene())
            scenes.append(BirthdayScene())

        if scene_type is None or scene_type is SceneType.ARTWORK:
            scenes.append(SnapshotScene())
            scenes.append(ChatGPTScene())
            scenes.append(ClockScene())

        if weighted is True:
            weighted_scenes = []
            for scene in scenes:
                for num in range(0, scene.weight):
                    weighted_scenes.append(scene)

            scenes = weighted_scenes

        return scenes

    def get_priorities(self):
        scenes = self.__all_scenes()
        res = []
        for scene in scenes:
            res.append({"scene": scene.__class__.__name__, "priority": scene.priority})
        return res

    def get_scene(self, scene_name) -> AbstractScene:
        scene = globals()[scene_name]()
        return scene
