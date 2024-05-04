#from .Demo import Scene
import random

from Scenes.Demo import Scene
from Repository import Repository
from vestaboard.formatter import Formatter

class SnapshotScene(Scene):
    def get_raw(self):
        entries = Repository().get_snapshots()
        random_index = random.randint(0, len(entries) - 1)
        print("random index: " + str(random_index))
        object = Repository().get_snapshot_object(entries[random_index])
        return object["raw"]