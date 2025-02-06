import datetime
import random
import uuid
from typing import Optional, Dict

import vesta

from Helper.ConfigHelper import ConfigHelper
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn

import json
from pprint import pprint
import random


from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)


class CountdownItem:
    def __init__(self, unique_id, title:str, date_string, background:str):
        self.id = unique_id
        self.title = title
        self.date = datetime.datetime.strptime(date_string, '%Y-%m-%d')

    id: str
    title:str
    date:datetime.datetime


class CountdownScene(AbstractScene):
    priority = 100
    overwritable = True

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()

        item = self.get_item(previous_identifier)

        if item is None:
            logger.error(f"No item was found for {previous_identifier}")
            return SceneExecuteReturn.error(f"No item was found for {previous_identifier}")

        message = "countdown scene " + item.title
        chars = vesta.encode_text(message, align="center", valign="middle")

        return SceneExecuteReturn(f"{self.__class__.__name__}_{item.id}_{start_date.strftime('%Y-%m-%d-%H:%M')}", True, self.priority, self,
                                  start_date, end_date, message, chars)


    # returns a configured countdown item. If an identifier is given the corresponding item will be returned.
    # If no identifier is given a random item will be returned.
    def get_item(self, previous_identifier: str = None) -> Optional[CountdownItem]:
        # Datei öffnen und JSON-Daten laden
        with open("/config/countdowns.json", "r", encoding="utf-8") as file:
            data = json.load(file)

            if previous_identifier:
                for item in data["items"]:
                    if item["id"] == previous_identifier.split("_")[1]:
                        return CountdownItem(item["id"], item["title"], item["date"], item["background"])
            else:
                # random item - no previous run was given
                length = len(data["items"])
                item = data["items"][random.randint(0, length - 1)]
                return CountdownItem(item["id"], item["title"], item["date"], item["background"])