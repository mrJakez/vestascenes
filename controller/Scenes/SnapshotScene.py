import random
import vesta
from Scenes.AbstractScene import AbstractScene
from Repository import Repository


class SnapshotScene(AbstractScene):
    def execute(self, vboard):
        entries = Repository().get_snapshots()
        random_index = random.randint(0, len(entries) - 1)
        object = Repository().get_snapshot_object(entries[random_index])

        if vboard.read_message() == object["raw"] and len(entries) > 1:
            print("!!!!!!!!!!!!!! Already displaying " + object["title"] + ". Iterate once more")
            self.execute(vboard)
            return

        vboard.write_message(object["raw"])

        print("random index: " + str(random_index) + "=> title: " + str(entries[random_index][0]))
        print("picked snapshot:")
        vesta.pprint(object["raw"])

        self.lastGeneratedMessage = object["title"]
