from Models.SceneInstanceModel import SceneInstanceModel
from Repository import SingletonMeta, Repository
from Helper.ConfigHelper import ConfigHelper
import vesta

from Scenes.AbstractScene import SceneExecuteReturn

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)

class VboardHelper(metaclass=SingletonMeta):
    _client: vesta.ReadWriteClient = None

    def get_client(self):
        if self._client is None:

            key = ConfigHelper.get_vboard_read_write_key()
            if key is not None and len(key) > 0 and key != "please_specify":
                self._client = vesta.ReadWriteClient(key)

        return self._client

    def is_initialized(self):
        return self.get_client() is not None

    def print(self, res: SceneExecuteReturn, send_to_board: bool = True):
        vboard = VboardHelper().get_client()

        if res.raw is None:
            logger.debug("empty raw")
            return

        vesta.pprint(res.raw)
        if send_to_board:
            try:
                Repository().unmark_active_scene_instance()
                model = SceneInstanceModel(scene_exec_return=res)
                Repository().save_scene_instance(model)

                vboard.write_message(res.raw)
            except Exception as exc:
                logger.error(f"HTTP Exception catched {exc}")