import datetime
import random
import uuid

import vesta
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn


class SnapshotScene(AbstractScene):

    def execute(self):

        entries = Repository().get_snapshots()

        if len(entries) is 0:
            return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", False, self.priority, self,
                                      None, None, "no snapshots found", None)

        #todo: final über die scene_isntances "is_active" finden
        vboard = vesta.ReadWriteClient("3e5dc670+a418+43f0+acd5+4ff8cc5fb2fd")

        random_index = random.randint(0, len(entries) - 1)
        snapshot_model = entries[random_index]

        if vboard.read_message() == snapshot_model.get_raw_list() and len(entries) > 1:
            print(f">>>>>>>>>>>>>>>>> Already displaying {snapshot_model.title} -> Iterate once more <<<<<<<<<<<<<<<<<<<<<<")
            return self.execute()

        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(minutes=60)

        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self, start_date, end_date, f"displaying {snapshot_model.title}", snapshot_model.get_raw_list())
