import datetime
import random
import uuid

import vesta

from Helper.ConfigHelper import ConfigHelper
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn


class NewReleaseScene(AbstractScene):
    priority = 300

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        # fetch prev version
        prev_hash = self.get_config('stored-hash')
        # fetch current version
        current_hash = ConfigHelper.get_git_hash()

        if prev_hash == current_hash:
            return SceneExecuteReturn.error(self, "no new version")

        self.save_config({'stored-hash': current_hash})

        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(minutes=5)
        message = f"new version #{current_hash} installed"
        chars = vesta.encode_text(message, align="center", valign="middle")

        return SceneExecuteReturn(f"{self.__class__.__name__}_{current_hash}", True, self.priority, self,
                                  start_date, end_date, message, chars)
