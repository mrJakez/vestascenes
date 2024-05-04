#from .Demo import Scene
import random

from Scenes.Demo import Scene
from Repository import Repository
from vestaboard.formatter import Formatter

class HistoryScene(Scene):
    def get_raw(self):
        entries = Repository().get_scenes()
        random_index = random.randint(0, len(entries) - 1)
        print("random index: " + str(random_index))
        object = Repository().get_scene_object(entries[random_index])
        return object["raw"]