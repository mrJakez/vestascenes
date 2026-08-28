from datetime import datetime, timedelta
from typing import Optional

import requests
import vesta

from Helper.Logger import setup_custom_logger
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from Scenes.StravaLastActivityScene import get_components


logger = setup_custom_logger(__file__)


class StravaProxyLastActivityScene(AbstractScene):
    """Render the latest activity through the local Strava proxy instead of Strava directly."""

    priority: int = 150
    overwritable = True

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        if not self.is_initialized():
            return SceneExecuteReturn.error(
                self,
                "Strava proxy not configured. Set proxy_url, proxy_api_key and account_identifier "
                "in config/settings.ini under [StravaProxyLastActivityScene].",
            )

        last_executed = self.get_last_executed()
        if not self.force_positive_rendering and last_executed and last_executed + timedelta(minutes=2) > datetime.now():
            return SceneExecuteReturn.error(self, f"Strava proxy not executed to protect rate limit ({last_executed})")

        try:
            last_activity = self.get_last_activity()
        except requests.RequestException as error:
            return SceneExecuteReturn.error(self, f"Strava proxy request failed: {error}")
        except (KeyError, TypeError, ValueError) as error:
            return SceneExecuteReturn.error(self, f"Strava proxy returned an invalid activity response: {error}")

        if not last_activity:
            return SceneExecuteReturn.error(self, "No Strava activities found for the configured account.")

        start_date_local = self.parse_datetime(last_activity["start_date_local"])
        activity_end_date = start_date_local + timedelta(seconds=last_activity["elapsed_time"])
        if not self.force_positive_rendering and datetime.now() - timedelta(hours=24) >= activity_end_date:
            self.store_last_executed(datetime.now())
            return SceneExecuteReturn.error(
                self,
                f"last Strava activity '{last_activity['name']}' is too old (start_date: {last_activity['start_date_local']})",
            )

        start_date = datetime.now()
        end_date = (start_date + timedelta(minutes=120)).replace(minute=0, second=0, microsecond=1)
        activity_type = last_activity.get("type") or last_activity.get("sport_type", "Activity")
        name = last_activity["name"]
        if activity_type == "EBikeRide":
            name = f"{name} {{67}}"

        moving_time = last_activity.get("moving_time", 0)
        hours, remainder = divmod(moving_time, 3600)
        minutes, _ = divmod(remainder, 60)
        props = {
            "name": name,
            "dist": f"{int((last_activity.get('distance') or 0) / 1000)}km",
            "avg": f"{(last_activity.get('average_speed') or 0) * 3.6:.1f} km/h",
            "time": f"{hours}h{minutes}m",
            "max": f"{(last_activity.get('max_speed') or 0) * 3.6:.1f} km/h",
            "elev": f"{int(last_activity.get('total_elevation_gain') or 0)}m",
            "hr": f"{int(last_activity['average_heartrate'])}bpm" if last_activity.get("average_heartrate") else "-",
            "watt": f"{int(last_activity['average_watts'])}w" if last_activity.get("average_watts") else "-",
            "cal": f"{int(last_activity['calories'])}" if last_activity.get("calories") else "-",
        }

        chars = vesta.VBMLClient().compose(get_components(), props)
        vesta.pprint(chars)
        self.store_last_executed(datetime.now())
        message = f"Strava proxy: {last_activity['name']} - {activity_type}"
        logger.info("id: %s - %s", last_activity["id"], message)
        return SceneExecuteReturn(
            f"{self.__class__.__name__}_{last_activity['id']}_{last_activity['name']}",
            True,
            self.priority,
            self,
            start_date,
            end_date,
            message,
            chars,
        )

    def get_last_activity(self):
        headers = {"Authorization": f"Bearer {self.get_config('proxy_api_key')}"}
        base_url = self.get_config("proxy_url").rstrip("/")
        account = self.get_config("account_identifier")
        response = requests.get(f"{base_url}/{account}/activities", headers=headers, params={"per_page": 1}, timeout=20)
        response.raise_for_status()
        summaries = response.json()
        if not summaries:
            return None
        response = requests.get(f"{base_url}/{account}/activities/{summaries[0]['id']}", headers=headers, timeout=20)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def parse_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)

    @staticmethod
    def is_initialized() -> bool:
        config = StravaProxyLastActivityScene().get_config()
        return all(config.get(key) for key in ("proxy_url", "proxy_api_key", "account_identifier"))

    def get_last_executed(self) -> Optional[datetime]:
        value = self.get_config("last_executed")
        return datetime.fromisoformat(value) if value else None

    def store_last_executed(self, last_executed: datetime):
        self.save_config({"last_executed": last_executed.isoformat()})
