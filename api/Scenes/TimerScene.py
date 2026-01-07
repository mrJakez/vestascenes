import datetime
import uuid
from typing import Optional
from vesta.chars import Rows
import vesta

from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn

class TimerItem:
    timer_id: str
    template:str
    title:str
    end_date: datetime = None

    def __init__(self, timer_id:str=str(uuid.uuid4()), template:str="default", title:str="Timer", run_duration_seconds:int=10):
        self.timer_id = timer_id
        self.template = template
        self.title = title
        self.end_date = datetime.datetime.now() + datetime.timedelta(seconds=run_duration_seconds)

    @classmethod
    def from_scene_identifier(cls, identifier: str):
        """
        Erstellt ein TimerItem aus einem String Format:
        Timer_{id}_{template}_{title}_{duration}
        """
        if not identifier or not identifier.startswith("Timer_"):
            return None

        parts = identifier.split("_")
        if len(parts) < 5:
            return None

        item = TimerItem()
        item.timer_id = parts[1]
        item.template = parts[2]
        item.title = parts[3]
        item.end_date = datetime.datetime.fromtimestamp(float(parts[4]))
        return item


    def get_scene_identifier(self) -> str:
        return f"Timer_{self.timer_id}_{self.template}_{self.title}_{self.end_date.timestamp()}"

    def get_duration_in_min_and_seconds(self) -> str:
        remaining = self.end_date - datetime.datetime.now()
        total_seconds = int(remaining.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02}:{seconds:02}"


class TimerScene(AbstractScene):
    priority: int = 175
    overwritable = True

    timer_id: str = str(uuid.uuid4())
    template: str = "default"
    title: str = "Timer"
    run_duration_seconds: int = 10

    def get_item(self, previous_identifier: str = None) -> Optional[TimerItem]:
        if previous_identifier is not None:
            return TimerItem.from_scene_identifier(previous_identifier)
        else:
            return TimerItem(self.timer_id, self.template, self.title, self.run_duration_seconds)

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        now = datetime.datetime.now()
        item = self.get_item(previous_identifier)

        chars = vesta.encode_text(f"{item.title} -- {item.get_duration_in_min_and_seconds()}", align="center", valign="middle")

        return SceneExecuteReturn(
            item.get_scene_identifier(),
            True, 
            self.priority, 
            self, 
            now, 
            item.end_date,
            f"Timer Scene {item.title} ({item.timer_id})",
            chars
        )
