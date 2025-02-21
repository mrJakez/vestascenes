from datetime import datetime
import random
import uuid
from typing import Optional, Dict
from typing import List

import vesta
from vesta.chars import Rows

from Helper.ConfigHelper import ConfigHelper
from Helper.RawHelper import RawHelper
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn

import json
from pprint import pprint
import random
from vesta.vbml import Component


from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)


class CountdownItem:

    id: str
    title:str
    date:datetime
    background:str
    background_width:int

    def __init__(self, unique_id, title:str, date_string, background:str, background_width:int):
        self.id = unique_id
        self.title = title
        self.date = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        self.background = background
        self.background_width = background_width

    def get_raw_background(self) -> List:
        return RawHelper.get_raw_object(self.background)

    def get_days_hours_minutes(self) -> []:
        difference = self.date - datetime.now()

        days = difference.days
        hours, seconds = divmod(difference.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        return [days, hours, minutes, seconds]

    def get_days_hours_minutes_strings(self):
        days, hours, minutes, seconds = self.get_days_hours_minutes()
        max_length = max(len(str(days)), len(str(hours)), len(str(minutes)), len(str(seconds)))

        days_str = str(days).rjust(max_length).replace(' ', '{70}')
        hours_str = str(hours).rjust(max_length).replace(' ', '{70}')
        minutes_str = str(minutes).rjust(max_length).replace(' ', '{70}')
        seconds_str = str(seconds).rjust(max_length).replace(' ', '{70}')

        return [days_str, hours_str, minutes_str, seconds_str]


class CountdownScene(AbstractScene):
    priority = 100
    overwritable = True

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        start_date = datetime.now()
        end_date = self.get_next_full_hour()
        item = self.get_item(previous_identifier)

        if item is None:
            logger.error(f"No item was found for {previous_identifier}")
            return SceneExecuteReturn.error(f"No item was found for {previous_identifier}")

        days_hours_min = item.get_days_hours_minutes()
        countdownstring = f"Verbleibende Zeit: {days_hours_min[0]} Tage, {days_hours_min[1]} Stunden, {days_hours_min[2]} Minuten, {days_hours_min[3]} Sekunden"
        message = "countdown scene " + item.title + countdownstring
        chars = self.get_chars(item)

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
                        return CountdownItem(item["id"], item["title"], item["date"], item["background"], item["background-width"])
            else:
                # random item - no previous run was given
                length = len(data["items"])
                item = data["items"][random.randint(0, length - 1)]
                return CountdownItem(item["id"], item["title"], item["date"], item["background"], item["background-width"])


    # noinspection PyMethodMayBeStatic
    def get_chars(self, item: CountdownItem) -> Rows:
        components = [
            Component(
                template="{{title}}",
                justify="left",
                align="top",
                height=1,
                width= (22 - item.background_width),
                absolute_position={
                    "x": item.background_width,
                    "y": 1
                }
            ),
            Component(
                template="{{days}} Tage",
                justify="left",
                align="top",
                height=1,
                width= (22 - item.background_width),
                absolute_position={
                    "x": item.background_width,
                    "y": 2
                }
            ),
            Component(
                template="{{hours}} Stunden",
                justify="left",
                align="top",
                height=1,
                width= (22 - item.background_width),
                absolute_position={
                    "x": item.background_width,
                    "y": 3
                }
            ),
            Component(
                template="{{minutes}} Minuten",
                justify="left",
                align="top",
                height=1,
                width= (22 - item.background_width),
                absolute_position={
                    "x": item.background_width,
                    "y": 4
                }
            ),
            Component(
                raw_characters=item.get_raw_background()
            )
        ]

        vbml_client = vesta.VBMLClient()
        day_hour_min_str = item.get_days_hours_minutes_strings()
        return vbml_client.compose(components, {
            "title": item.title,
            "days": day_hour_min_str[0],
            "hours": day_hour_min_str[1],
            "minutes": day_hour_min_str[2]
        })
