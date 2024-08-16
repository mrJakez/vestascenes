import datetime
import string
import os.path
import random

import vesta
from icalendar import Calendar
from vesta.chars import Rows

from Helper.RawHelper import RawHelper
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from vesta.vbml import Component


class BirthdayEntry:
    birthdate: datetime
    today: datetime
    person: string

    def __init__(self, component: Calendar, today: datetime):
        self.today = today

        birthdate = component.decoded('dtstart')
        summary = component.get('summary')

        self.birthdate = birthdate
        self.person = RawHelper.replace_umlaute(summary)

    def get_days_till_birthday_this_year(self):
        birthdate_in_current_year = self.birthdate.replace(year=self.today.year)
        days_inbetween = (birthdate_in_current_year - self.today).days
        return days_inbetween

    def get_new_age(self):
        return self.today.year - self.birthdate.year

    def __str__(self):
        name = self.person
        if len(name) > 15:
            name = name[0:15]

        return f'{name} ({self.get_new_age()})'


class BirthdayScene(AbstractScene):
    priority: int = 130

    def get_blacklist(self):
        string_list = self.get_config('blacklist')
        arr = string_list.split(',')
        stripped = list(map(str.strip, arr))
        return stripped

    def execute(self, vboard) -> SceneExecuteReturn:
        if not os.path.isfile("/config/birthdays.ics"):
            return SceneExecuteReturn.error(self, "/config/birthdays.ics does not exist")

        g = open('/config/birthdays.ics', 'rb')
        gcal = Calendar.from_ical(g.read())
        today = datetime.date.today()

        # today = datetime.date.today().replace(month=2, day=3)

        blacklist = self.get_blacklist()
        message = []
        entries = []
        for component in gcal.walk():
            if component.name != "VEVENT":
                continue

            entry = BirthdayEntry(component, today)

            if entry.person in blacklist:
                continue

            if entry.get_days_till_birthday_this_year() < 0:
                # birthday was already within the current year
                continue

            if entry.get_days_till_birthday_this_year() > 0:
                # birthday is far in the future - ignore it here
                continue

            entries.append(entry)
            message.append(str(entry))

        chars = None

        if len(entries) == 0:
            return SceneExecuteReturn.error(self, "No birthdays present today")
        elif len(entries) == 1:
            chars = self.get_single_entry_chars(entries[0])
        elif 1 < len(entries) < 5:
            chars = self.get_multi_entry_chars(entries)
        else:
            return SceneExecuteReturn.error(self, f"No matching preset found ({len(entries)} birthday items)")

        start_date = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=1)
        end_date = start_date + datetime.timedelta(hours=12)  # should be visible the whole day

        return SceneExecuteReturn(f"birthday_{start_date.strftime('%Y-%m-%d')}", True, self.priority, self,
                                  start_date, end_date, ", ".join(message), chars)

    # noinspection PyMethodMayBeStatic
    def get_single_entry_chars(self, entry: BirthdayEntry) -> Rows:

        cake = [[0, 0, 65, 0, 65, 0, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 66, 0, 67, 0, 68, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 65, 65, 65, 65, 65, 65, 65, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0],
                [0, 64, 64, 64, 64, 64, 64, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 63, 63, 63, 63, 63, 63, 63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        bow = [[0, 67, 67, 67, 0, 64, 64, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 67, 67, 63, 63, 63, 64, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 65, 63, 63, 63, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 65, 0, 65, 0, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 65, 0, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        balon = [[0, 0, 63, 63, 63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 63, 63, 63, 69, 63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 63, 63, 63, 63, 63, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 63, 63, 63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        gift = [[0, 65, 65, 0, 0, 0, 65, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 65, 65, 65, 0, 65, 65, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [67, 67, 67, 67, 65, 67, 67, 67, 67, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [67, 67, 67, 67, 65, 67, 67, 67, 67, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [67, 67, 67, 67, 65, 67, 67, 67, 67, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [67, 67, 67, 67, 65, 67, 67, 67, 67, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        artwork = random.choice([cake, bow, balon, gift])

        components = [
            Component(
                template="Happy",
                justify="left",
                align="top",
                height=1,
                width=13,
                absolute_position={
                    "x": 9,
                    "y": 1
                }
            ),
            Component(
                template="Birthday,",
                justify="left",
                align="top",
                height=1,
                width=13,
                absolute_position={
                    "x": 9,
                    "y": 2
                }
            ),
            Component(
                template="{{name}}",
                justify="left",
                align="top",
                height=1,
                width=13,
                absolute_position={
                    "x": 9,
                    "y": 3
                }
            ),
            Component(
                template="Alter: {{age}}",
                justify="left",
                align="top",
                height=1,
                width=13,
                absolute_position={
                    "x": 9,
                    "y": 4
                }
            ),
            Component(
                raw_characters=artwork
            )
        ]

        vbml_client = vesta.VBMLClient()
        return vbml_client.compose(components, {"name": entry.person[:13], "age": entry.get_new_age()})

    # noinspection PyMethodMayBeStatic
    def get_multi_entry_chars(self, entries: [BirthdayEntry]) -> Rows:
        props = None
        if len(entries) == 2:
            props = {
                "line1": f"Happy Birthday",
                "line2": f"{entries[0]}",
                "line3": f"{entries[1]}",
                "line4": f"",
            }
        elif len(entries) == 3:
            props = {
                "line1": f"Happy Birthday",
                "line2": f"{entries[0]}",
                "line3": f"{entries[1]}",
                "line4": f"{entries[2]}",
            }
        elif len(entries) == 4:
            props = {
                "line1": f"{entries[0]}",
                "line2": f"{entries[1]}",
                "line3": f"{entries[2]}",
                "line4": f"{entries[3]}",
            }
        components = [
            Component(
                template="{{line1}}",
                justify="center",
                align="top",
                height=1,
                width=20,
                absolute_position={
                    "x": 1,
                    "y": 1
                }
            ),
            Component(
                template="{{line2}}",
                justify="center",
                align="top",
                height=1,
                width=20,
                absolute_position={
                    "x": 1,
                    "y": 2
                }
            ),
            Component(
                template="{{line3}}",
                justify="center",
                align="top",
                height=1,
                width=20,
                absolute_position={
                    "x": 1,
                    "y": 3
                }
            ),
            Component(
                template="{{line4}}",
                justify="center",
                align="top",
                height=1,
                width=20,
                absolute_position={
                    "x": 1,
                    "y": 4
                }
            ),
            Component(
                raw_characters=[
                    [63, 64, 65, 66, 67, 68, 63, 64, 65, 66, 67, 68, 63, 64, 65, 66, 67, 68, 63, 64, 65, 66],
                    [64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 67],
                    [65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 68],
                    [66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 63],
                    [67, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64],
                    [68, 63, 64, 65, 66, 67, 68, 63, 64, 65, 66, 67, 68, 63, 64, 65, 66, 67, 68, 63, 64, 65]
                ]
            )
        ]
        vbml_client = vesta.VBMLClient()
        return vbml_client.compose(components, props)
