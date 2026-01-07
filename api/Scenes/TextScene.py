import datetime
import random
import uuid

import vesta

from Helper.ConfigHelper import ConfigHelper
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from typing import List

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)

class TextScene(AbstractScene):
    priority = 180
    text: str = None
    raw: List = None

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()

        chars = None
        out_message:str = ""

        if self.raw is not None:
            chars = self.raw
            out_message = "Defined by raw"
        elif self.text is not None:
            chars = vesta.encode_text(self.text, align="center", valign="middle")
            out_message = f"Defined by text: {self.text}"
        else:
            return SceneExecuteReturn.error(self, "try to initiate a TextScene without raw and text value")

        return SceneExecuteReturn(f"{self.__class__.__name__}_{start_date.strftime('%Y-%m-%d-%H:%M')}", True, self.priority, self,
                                  start_date, end_date, out_message, chars)