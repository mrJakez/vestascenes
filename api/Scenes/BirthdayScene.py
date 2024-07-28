import datetime
import random
import string
import uuid
import os.path
import vesta
from icalendar import Calendar
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
        self.person = summary

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

    def execute(self):
        if not os.path.isfile("/config/birthdays.ics"):
            return SceneExecuteReturn.error(self, "/config/birthdays.ics does not exist")

        g = open('/config/birthdays.ics', 'rb')
        gcal = Calendar.from_ical(g.read())
        today = datetime.date.today()

        #today = datetime.date.today().replace(month=7, day=21)
        #22.2 => two person,  4.3 => three person, 3.2 => four person

        message = []
        entries = []
        for component in gcal.walk():
            if component.name != "VEVENT":
                continue

            entry = BirthdayEntry(component, today)

            if entry.get_days_till_birthday_this_year() < 0:
                # birthday was already within the current year
                continue

            if entry.get_days_till_birthday_this_year() > 0:
                # birthday is far in the future - ignore it here
                continue

            entries.append(entry)
            message.append(str(entry))

        if len(entries) == 0:
            return SceneExecuteReturn.error(self, "No birthdays present today")
        elif len(entries) == 1:
            props = {
                "line1": f"",
                "line2": f"Happy Birthday",
                "line3": f"{entries[0]}",
                "line4": f"",
            }
        elif len(entries) == 2:
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

        if 'props' not in locals():
            return SceneExecuteReturn.error(self, f"No matching preset found ({len(entries)} birthday items)")

        vbml_client = vesta.VBMLClient()
        chars = vbml_client.compose(self.get_vbml(), props)

        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour() + datetime.timedelta(hours=12)  # should be visible the whole day

        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", False, self.priority, self,
                                  start_date, end_date, ", ".join(message), chars)

    def get_vbml(self):
        return [
            Component(
                template="{63}{64}{65}{66}{67}{68}{63}{64}{65}{66}{67}{68}{63}{64}{65}{66}{67}{68}{63}{64}{65}{66}",
                justify="center",
                align="top",
                height=1,
                width=22
            ),
            Component(
                template="{64}",
                justify="center",
                align="top",
                height=1,
                width=1
            ),
            Component(
                template="{{line1}}",
                justify="center",
                align="top",
                height=1,
                width=20
            ),
            Component(
                template="{67}",
                justify="center",
                align="top",
                height=1,
                width=1
            ),
            Component(
                template="{65}",
                justify="center",
                align="top",
                height=1,
                width=1
            ),
            Component(
                template="{{line2}}",
                justify="center",
                align="top",
                height=1,
                width=20
            ),
            Component(
                template="{68}",
                justify="center",
                align="top",
                height=1,
                width=1
            ),
            Component(
                template="{66}",
                justify="center",
                align="top",
                height=1,
                width=1
            ),
            Component(
                template="{{line3}}",
                justify="center",
                align="top",
                height=1,
                width=20
            ),
            Component(
                template="{63}",
                justify="center",
                align="top",
                height=1,
                width=1
            ),
            Component(
                template="{67}",
                justify="center",
                align="top",
                height=1,
                width=1
            ),
            Component(
                template="{{line4}}",
                justify="center",
                align="top",
                height=1,
                width=20
            ),
            Component(
                template="{64}",
                justify="center",
                align="top",
                height=1,
                width=1
            ),
            Component(
                template="{68}{63}{64}{65}{66}{67}{68}{63}{64}{65}{66}{67}{68}{63}{64}{65}{66}{67}{68}{63}{64}{65}",
                justify="center",
                align="top",
                height=1,
                width=22
            )
        ]