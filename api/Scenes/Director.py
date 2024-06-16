import random
from Scenes.AbstractScene import AbstractScene
from Scenes.SnapshotScene import SnapshotScene
from Scenes.ChatGPTScene import ChatGPTScene
from Scenes.StravaLastActivityScene import StravaLastActivityScene
from Scenes.WasteCalendarScene import WasteCalendarScene
from Scenes.AbstractScene import SceneType
from Repository import Repository

class Director:

    def  get_next_scene(self) -> AbstractScene:

        returns = []
        for timed_scene in self.__all_scenes(SceneType.TIMED):

            execute_res = timed_scene.execute()

            if execute_res.should_execute is True and Repository().scene_instances_with_id_exists(execute_res.id) is False:
                returns.append(execute_res)

        # order SceneExecuteReturn objects based on priority
        returns.sort(key=lambda x: x.priority, reverse=True)

        if len(returns) > 0:
            print("Director: found a TIMED scene")
            return returns[0]
        else:
            artwork_scene = random.choice(self.__all_scenes(SceneType.ARTWORK))
            return artwork_scene.execute()


    def __all_scenes(self, scene_type = None) -> AbstractScene:

        scenes = []  # empty array

        if scene_type is None or scene_type is SceneType.TIMED:
            scenes.append(WasteCalendarScene())
            scenes.append(StravaLastActivityScene())

        if scene_type is None or scene_type is SceneType.ARTWORK:
            scenes.append(SnapshotScene())
            scenes.append(ChatGPTScene())

        return scenes


    def get_priorities(self):
        scenes = self.__all_scenes()
        res = []
        for scene in scenes:
            res.append({"scene":scene.__class__.__name__, "priority": scene.priority})
        return res