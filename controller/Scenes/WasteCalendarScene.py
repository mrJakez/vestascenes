from datetime import date

from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from icalendar import Calendar, Event
import requests
import datetime
import vesta

class WasteCalendarScene(AbstractScene):

    priority: int = 200

    def __init__(self):
        super().__init__()
        today = datetime.date.today()

        if today.weekday() != 6:
            self.lastGeneratedMessage = "current day is not Sunday"
            self.scene_enabled = False


    def execute(self):
        url = "https://gelsendienste.abisapp.de/abfuhrkalender?format=ical&street=0E1F25F8&number=21"
        file = requests.get(url).text
        gcal = Calendar.from_ical(file)

        today = datetime.date.today()
        identifier = f"{self.__class__.__name__}_{(today + datetime.timedelta(weeks=5)).strftime("%Y-cw%V")}"

        if today.weekday() != 6:
            return SceneExecuteReturn(identifier, False, self.priority, self, None, None, "Es ist nicht Sonntags", None)

        friday_next_week: date = today + datetime.timedelta(days=5)
        todos = []

        for component in gcal.walk():
            if component.name == "VEVENT":
                dstart = component.decoded('dtstart')
                summary = component.get('summary')

                if summary == "Braune Tonne":
                    continue

                if dstart >= today and dstart <= friday_next_week:
                    todos.append(f"{dstart}: {summary}")

                #print(f"{dstart} : {summary}")

        message = "|| ".join(todos)

        chars = vesta.encode_text(
            message,
            valign="middle",
        )

        # todo: muss ab Sonntag 17:00 uhr angepinnt werden
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(minutes=2)
        print(f"gebe eine WasteCalendarScene mit prio {self.priority} zurück")
        return SceneExecuteReturn(identifier, True, self.priority, self, start_date, end_date, f"{message}", chars)