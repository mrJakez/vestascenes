import random
from Scenes.AbstractScene import AbstractScene
from Scenes.SnapshotScene import SnapshotScene
from Scenes.ChatGPTScene import ChatGPTScene
from Scenes.WasteCalendarScene import WasteCalendarScene


class Director:
    def find_best_scene(self) -> AbstractScene:
        scenes = self.__all_scenes()

        scene = self.__pick_scene(scenes)

        print(f"scene found {scene.scene_enabled}")

        while scene.scene_enabled is False:
            print("scene enabled = FALSE")
            scene = self.__pick_scene(scenes.remove(scene))

        print("scene found")
        return scene

    def __pick_scene(self, scenes_array) -> AbstractScene:
        current_scene = random.choice(scenes_array)
        return current_scene

    def __all_scenes(self):
        scenes = []  # empty array
        scenes.append(WasteCalendarScene())
        scenes.append(SnapshotScene())
        scenes.append(ChatGPTScene())
        return scenes
