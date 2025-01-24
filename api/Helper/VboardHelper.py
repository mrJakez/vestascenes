from Repository import SingletonMeta
from Helper.ConfigHelper import ConfigHelper
import vesta


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
