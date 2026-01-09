from Models.SceneInstanceModel import SceneInstanceModel
from Repository import SingletonMeta, Repository
from Helper.ConfigHelper import ConfigHelper
import vesta

from Scenes.AbstractScene import SceneExecuteReturn

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)

class VboardHelper(metaclass=SingletonMeta):
    _client: vesta.ReadWriteClient = None
    _local_client: vesta.LocalClient = None

    def get_client(self):
        if ConfigHelper.get_vboard_read_write_key() is not None:
            if self._client is None:
                key = ConfigHelper.get_vboard_read_write_key()
                if key is not None and len(key) > 0 and key != "please_specify":
                    self._client = vesta.ReadWriteClient(key)

            return self._client
        elif ConfigHelper.get_vboard_local_api_key() is not None and ConfigHelper.get_vboard_local_url() is not None:
            if self._local_client is None:
                api_key = ConfigHelper.get_vboard_local_api_key()
                url = ConfigHelper.get_vboard_local_url()

                self._local_client = vesta.LocalClient(local_api_key=api_key, base_url=url)

            return self._local_client

        logger.error(f"No valid vesta configuration found.")
        return None

    def is_initialized(self):
        if self._client is not None or self._local_client is not None:
            return True
        return False

    def print(self, res: SceneExecuteReturn, send_to_board: bool = True):
        vboard = self.get_client()

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