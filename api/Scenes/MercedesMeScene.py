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

    # Übergabedatum deines Wagens
    sternchen_purchase_date = datetime.date(2025, 3, 3)

    # Vertragsparameter
    annual_allowance_km = 25_000
    term_years = 3


    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()

        odometer_km = self._get_odo()
        state_of_charge = self._get_state_of_charge()

        if odometer_km == -1:
            return SceneExecuteReturn.error(self, f"We had problems to fetch the current km from mercedes-me)")

        # ---- Soll/Ist berechnen ----
        res = self._km_delta_vs_allowance(
            purchase_date=self.sternchen_purchase_date,
            current_odometer_km=odometer_km,
            annual_allowance_km=self.annual_allowance_km,
            term_years=self.term_years,
        )

        # Werte runden/aufbereiten
        allowed_to_date = round(res["allowed_to_date_km"])
        over_under = round(res["over_under_km"])  # >0 = drüber, <0 = drunter
        sign = "+" if over_under > 0 else ""
        progress = round(res["progress_pct"], 1)

        message = (
            "Sternchen Status\n\n"
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

    @staticmethod
    def _add_years(d: datetime.date, years: int) -> datetime.date:
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            # 29.02. -> 28.02. im Zieljahr
            return d.replace(month=2, day=28, year=d.year + years)

    def _km_delta_vs_allowance(
        self,
        purchase_date: datetime.date,
        current_odometer_km: float,
        annual_allowance_km: float,
        term_years: int,
        today: datetime.date | None = None,
    ) -> dict:
        if today is None:
            today = datetime.date.today()

        start = purchase_date
        end = self._add_years(start, term_years)
        total_allowance = annual_allowance_km * term_years

        if end <= start:
            raise ValueError("Laufzeitende liegt nicht nach dem Start.")

        total_days = (end - start).days
        elapsed_days = (min(today, end) - start).days
        elapsed_days = max(elapsed_days, 0)
        progress = elapsed_days / total_days  # 0..1

        allowed_to_date = total_allowance * progress
        over_under_km = current_odometer_km - allowed_to_date
        over_under_pct = (over_under_km / allowed_to_date * 100) if allowed_to_date > 0 else float("inf")

        remaining_days = (end - today).days if today < end else 0
        remaining_km = max(total_allowance - current_odometer_km, 0)

        return {
            "start": start,
            "end": end,
            "today": today,
            "total_allowance_km": total_allowance,
            "allowed_to_date_km": allowed_to_date,
            "over_under_km": over_under_km,        # >0 = drüber
            "over_under_pct": over_under_pct,
            "remaining_days": remaining_days,
            "remaining_km_total_left": remaining_km,
            "progress_pct": progress * 100.0,
        }