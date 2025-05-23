import datetime
from datetime import date
from enum import Enum
from typing import List

import requests
import vesta
from icalendar import Calendar
from vesta.vbml import Component

from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn


# class syntax
class WasteType(Enum):
    GRAY = 1
    YELLOW = 2
    BLUE = 3

    def get_vbml_code(self):
        if self == WasteType.GRAY:
            return '69'
        elif self == WasteType.YELLOW:
            return '65'
        elif self == WasteType.BLUE:
            return '67'

    def __str__(self):
        if self == WasteType.GRAY:
            return 'Graue'
        elif self == WasteType.YELLOW:
            return 'Gelbe'
        elif self == WasteType.BLUE:
            return 'Blaue'


class WasteEntry:
    date: datetime
    type: WasteType

    def __init__(self, component: Calendar):
        dstart = component.decoded('dtstart')
        summary = component.get('summary')

        # noinspection PyTypeChecker
        current_type: WasteType = None

        if summary == "Graue Tonne":
            current_type = WasteType.GRAY
        elif summary == "Gelbe Tonne":
            current_type = WasteType.YELLOW
        elif summary == "Blaue Tonne":
            current_type = WasteType.BLUE

        self.date = dstart
        self.type = current_type

    def __str__(self):
        return f'{self.type} - {self.date_str()}'

    def date_str(self):
        return self.date.strftime('%d.%m (%a)')


class WasteCalendarScene(AbstractScene):
    priority: int = 200

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        today = datetime.datetime.now()
        calendarweek = (today + datetime.timedelta(weeks=5)).strftime("%V")
        identifier = f"{self.__class__.__name__}_{(today + datetime.timedelta(weeks=5)).strftime('%Y-cw%V')}"

        if self.force_positive_rendering == False and today.weekday() != 6:
            return SceneExecuteReturn.error(self, "Will just check waste calendar on Sunday")

        url = "https://gelsendienste.abisapp.de/abfuhrkalender?format=ical&street=0E1F25F8&number=21"
        file = requests.get(url).text
        gcal = Calendar.from_ical(file)

        friday_next_week: date = today.date() + datetime.timedelta(days=5)
        todos: List[WasteEntry] = []

        for component in gcal.walk():
            if component.name != "VEVENT":
                continue

            entry = WasteEntry(component)
            if entry.type is not None and today.date() <= entry.date <= friday_next_week:
                todos.append(entry)

        all_components = [Component(
            template=f"Abfallkalender - KW{calendarweek}",
            justify="center",
            align="top",
            height=2,
            width=22
        )]

        messages = []
        for todo in todos:
            all_components.extend(self.get_todo_vbml_components(todo))
            messages.append(str(todo))

        message = ', '.join(messages)
        vbml_client = vesta.VBMLClient()
        chars = vbml_client.compose(all_components)

        start_date = datetime.datetime.now().replace(hour=15, minute=0, second=0, microsecond=1)
        end_date = start_date + datetime.timedelta(hours=6)  # starts 15:00. will be present till 21:00

        return SceneExecuteReturn(identifier, True, self.priority, self, start_date, end_date, f"{message}", chars)

    # noinspection PyMethodMayBeStatic
    def get_todo_vbml_components(self, entry: WasteEntry) -> List[Component]:
        icon_component = Component(
            template="{" + str(entry.type.get_vbml_code()) + "}",
            justify="left",
            align="top",
            height=1,
            width=2
        )

        label_component = Component(
            template=f"{str(entry.type)}",
            justify="left",
            align="top",
            height=1,
            width=6
        )

        date_component = Component(
            template=f"{str(entry.date_str())}",
            justify="left",
            align="top",
            height=1,
            width=14
        )
        return [icon_component, label_component, date_component]
