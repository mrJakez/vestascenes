import datetime
import random
import uuid

import vesta

from Helper.ConfigHelper import ConfigHelper
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn


class ClockScene(AbstractScene):
    priority = 100
    overwritable = True

    def execute(self, vboard) -> SceneExecuteReturn:

        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()

        message = start_date.strftime("%H:%M")
        chars = vesta.encode_text(message, align="center", valign="middle")

        return SceneExecuteReturn(f"{self.__class__.__name__}_{start_date.strftime('%Y-%m-%d-%H:%M')}", True, self.priority, self,
                                  start_date, end_date, message, chars)