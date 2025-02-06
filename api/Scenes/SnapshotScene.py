import datetime
import random
import uuid

from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)

class SnapshotScene(AbstractScene):
    weight = 3

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:

        entries = Repository().get_snapshots()

        if len(entries) is 0:
            return SceneExecuteReturn.error(self, "no snapshots found")

        random_index = random.randint(0, len(entries) - 1)
        snapshot_model = entries[random_index]

        if vboard.read_message() == snapshot_model.get_raw_list() and len(entries) > 1:
            logger.info(f">>>>>>>>>>>>>>>>> Already displaying {snapshot_model.title} -> Iterate once more <<<<<<<<<<<<<<<<<<<<<<")
            return self.execute(vboard)

        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()
    
        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self, start_date, end_date, f"displaying {snapshot_model.title}", snapshot_model.get_raw_list())
