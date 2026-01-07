import datetime
import uuid
from typing import Optional
from vesta.chars import Rows
import vesta

from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn

class TimerScene(AbstractScene):
    priority: int = 10  # Höhere Priorität als die Uhr
    overwritable = True

    template: str = "default"
    title: str = "Timer"
    run_duration_seconds: int = 10


    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        now = datetime.datetime.now()
        diff = self.target_time - now
        
        # Wenn der Timer abgelaufen ist
        if diff.total_seconds() <= 0:
            return SceneExecuteReturn(f"Timer_{self.timer_id}", False, self.priority, self, now, now, "Timer expired", None)

        # Zeit formatieren (HH:MM:SS)
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # VBML für die Anzeige (ähnlich wie deine ChatGPT-Anzeige)
        vbml_client = vesta.VBMLClient()
        component = vesta.vbml.Component(
            template=f"TIMER\n\n{time_str}",
            width=22,
            height=6,
            justify="center",
            align="center"
        )
        chars = vbml_client.compose([component])

        # Die Szene soll sich jede Sekunde (oder Minute) aktualisieren, bis sie abläuft
        # Wir setzen das Enddatum auf 'jetzt + 1 Minute' für den Cache/Director
        return SceneExecuteReturn(
            f"Timer_{self.timer_id}", 
            True, 
            self.priority, 
            self, 
            now, 
            now + datetime.timedelta(minutes=1), 
            f"Timer {time_str}", 
            chars
        )
