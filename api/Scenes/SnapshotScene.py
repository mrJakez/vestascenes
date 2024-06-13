import random
import string
import uuid
import vesta
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from Repository import Repository
from Helper.RawHelper import RawHelper
import datetime

class SnapshotScene(AbstractScene):

    def execute(self):

        #todo: final über die scene_isntances "is_active" finden
        vboard = vesta.ReadWriteClient("3e5dc670+a418+43f0+acd5+4ff8cc5fb2fd")

        entries = Repository().get_snapshots()
        random_index = random.randint(0, len(entries) - 1)
        object = {"title": entries[random_index][0], "raw": RawHelper.get_raw_object(entries[random_index][1])}

        if vboard.read_message() == object["raw"] and len(entries) > 1:
            print(f">>>>>>>>>>>>>>>>> Already displaying {object["title"]} -> Iterate once more <<<<<<<<<<<<<<<<<<<<<<")
            return self.execute()

        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(minutes=60)

        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self, start_date, end_date, f"displaying {object["title"]}", object["raw"])
