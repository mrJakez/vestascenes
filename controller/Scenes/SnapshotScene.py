import random
from Scenes.AbstractScene import AbstractScene
from Repository import Repository

class SnapshotScene(AbstractScene):
    def execute(self, vboard):
            entries = Repository().get_snapshots()
            random_index = random.randint(0, len(entries) - 1)
            print("random index: " + str(random_index) + "=> title: " + str(entries[random_index][0]))
            object = Repository().get_snapshot_object(entries[random_index])

            vboard.raw(object["raw"])
