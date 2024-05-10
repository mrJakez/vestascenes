from datetime import date

from Scenes.AbstractScene import AbstractScene
from icalendar import Calendar, Event
import requests
import datetime

class WasteCalendarScene(AbstractScene):

    def __init__(self):
        super().__init__()
        today = datetime.date.today()

        if today.weekday() != 6:
            self.lastGeneratedMessage = "current day is not Sunday"
            self.scene_enabled = False


    def execute(self, vboard):
        url = "https://gelsendienste.abisapp.de/abfuhrkalender?format=ical&street=0E1F25F8&number=21"
        file = requests.get(url).text
        gcal = Calendar.from_ical(file)

        today = datetime.date.today()

        if today.weekday() != 6:
            self.lastGeneratedMessage = "current day is not Sunday"
            self.scene_enabled = False
            return

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

                print(f"{dstart} : {summary}")

        self.lastGeneratedMessage =  "|| ".join(todos)
