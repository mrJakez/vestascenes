import datetime
import os.path
import random
import string

import requests
import vesta
from icalendar import Calendar
from vesta.chars import Rows

from Helper.RawHelper import RawHelper
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from vesta.vbml import Component

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)


class MercedesMeScene(AbstractScene):
    weight = 3

    hass_url = "http://home.imount.de"
    hass_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5ZGQ0NjUyYjI1YzU0MDQ5YTBmOTliZTQ4MTc4NTMzMiIsImlhdCI6MTc1ODgyODA1NywiZXhwIjoyMDc0MTg4MDU3fQ.oDdC3gNKm2_33DFij5AXddrKfWf03sm7_iHh0YiN4CY"

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()

        odometer_km = self._get_odo()
        state_of_charge = self._get_state_of_charge()

        if odometer_km == -1:
            return SceneExecuteReturn.error(self, f"We had problems to fetch the current km from mercedes-me)")

        # Werte runden/aufbereiten
        over_under = self._get_over_under()
        sign = "+" if float(over_under) > 0 else ""

        message = (
            "- Sternchen Status -\n\n"
            f"Energie: {state_of_charge}%\n"
            f"ODO: {int(odometer_km):,}km\n\n"
            f"{sign}{over_under}km vs Soll"
        )

        # Tausendertrennzeichen in deutsch (Punkte) – Vestaboard hat nur ASCII, daher entfernen wir ggf. Komma
        message = message.replace(",", ".")

        chars = vesta.encode_text(message, align="center", valign="middle")

        return SceneExecuteReturn(
            f"{self.__class__.__name__}_{start_date.strftime('%Y-%m-%d-%H:%M')}",
            True,
            self.priority,
            self,
            start_date,
            end_date,
            message,
            chars,
        )


    # ---- intern: Berechnung Soll/Ist ----
    def _get_state_of_charge(self) -> string:
        headers = {
            "Authorization": f"Bearer {self.hass_token}",
            "Content-Type": "application/json",
        }
        r_state_of_charge = requests.get(f"{self.hass_url}/api/states/sensor.d_cc209e_state_of_charge", headers=headers, timeout=10)
        r_state_of_charge.raise_for_status()
        return r_state_of_charge.json()['state']

    def _get_over_under(self) -> string:
        headers = {
            "Authorization": f"Bearer {self.hass_token}",
            "Content-Type": "application/json",
        }
        r_state_of_charge = requests.get(f"{self.hass_url}/api/states/sensor.sternchen_overunder_km", headers=headers, timeout=10)
        r_state_of_charge.raise_for_status()
        return r_state_of_charge.json()['state']

    def _get_odo(self) -> float:
        headers = {
            "Authorization": f"Bearer {self.hass_token}",
            "Content-Type": "application/json",
        }

        r_odo = requests.get(f"{self.hass_url}/api/states/sensor.sternchen_odometer", headers=headers, timeout=10)
        r_odo.raise_for_status()
        data_odo = r_odo.json()

        # State kann string sein -> in float wandeln
        try:
            return float(str(data_odo["state"]).replace(",", "."))
        except (ValueError, KeyError) as e:
            logger.error(f"ODO API-error for value: {data_odo["state"]}")
            return -1
