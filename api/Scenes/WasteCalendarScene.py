import datetime
from datetime import date
from enum import Enum
from typing import TypedDict, List

import requests
import vesta
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from icalendar import Calendar
from vesta.vbml import Component


# class syntax
class WasteType(Enum):
    GRAY = 1
    YELLOW = 2
    BLUE = 3


class WasteEntry(TypedDict):
    date: datetime
    type: WasteType


class WasteCalendarScene(AbstractScene):
    priority: int = 200

    def execute(self):
        url = "https://gelsendienste.abisapp.de/abfuhrkalender?format=ical&street=0E1F25F8&number=21"
        file = requests.get(url).text
        gcal = Calendar.from_ical(file)

        today = datetime.date.today()
        identifier = f"{self.__class__.__name__}_{(today + datetime.timedelta(weeks=5)).strftime("%Y-cw%V")}"

        #if today.weekday() != 6:
        #    return SceneExecuteReturn(identifier, False, self.priority, self, None, None, "Es ist nicht Sonntags", None)

        friday_next_week: date = today + datetime.timedelta(days=5)
        todos:List[WasteEntry] = []

        for component in gcal.walk():
            if component.name == "VEVENT":
                dstart = component.decoded('dtstart')
                summary = component.get('summary')

                type:WasteType = None

                if summary == "Braune Tonne":
                    continue
                elif summary == "Graue Tonne":
                    type = WasteType.GRAY
                elif summary == "Gelbe Tonne":
                    type = WasteType.YELLOW
                elif summary == "Blaue Tonne":
                    type = WasteType.BLUE


                if dstart >= today and dstart <= friday_next_week:
                    item = WasteEntry(date=dstart, type=type)
                    todos.append(item)

                #print(f"{dstart} : {summary}")

        message = "kommt noch!"
        print(todos)



        vbml_client = vesta.VBMLClient()

        all_components = []

        header = Component(
            template="Abfallkalender",
            justify="center",
            align="top",
            height=2,
            width=22
        )
        all_components.append(header)

        for todo in todos:
            all_components.extend(self.get_todo_vbml_components(todo))

        chars = vbml_client.compose(all_components)

        # todo: muss ab Sonntag 17:00 uhr angepinnt werden
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(minutes=60)
        print(f"gebe eine WasteCalendarScene mit prio {self.priority} zurück")
        return SceneExecuteReturn(identifier, True, self.priority, self, start_date, end_date, f"{message}", chars)

    def get_todo_vbml_components(self, entry:WasteEntry) -> List[Component]:
        icon_component = Component(
            template="{67}",
            justify="left",
            align="top",
            height=1,
            width=2
        )
        label_component = Component(
            template="Blaue Tonne",
            justify="left",
            align="top",
            height=1,
            width=12
        )

        date_component = Component(
            template="dienstag",
            justify="left",
            align="top",
            height=1,
            width=8
        )
        return [icon_component, label_component, date_component]