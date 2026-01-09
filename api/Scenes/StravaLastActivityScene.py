from datetime import datetime, timedelta
from typing import Optional

import vesta
from stravalib import Client, unithelper
from stravalib.exc import RateLimitExceeded, Fault
from vesta.vbml import Component

from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)

def get_components():
    top_row = Component(
        "{63}{63}      Strava      {63}{63}",
        justify="center",
        align="top",
        height=1
    )
    second_row_left_icon = Component(
        "{63}",
        width=1,
        height=1
    )
    name = Component(
        "{{name}}",
        justify="center",
        width=20,
        height=1
    )
    second_row_right_icon = Component(
        "{63}",
        width=1,
        height=1
    )
    distance_label = Component(
        template="dist",
        justify="left",
        height=1,
        width=5
    )
    distance_value = Component(
        template="{{dist}}",
        justify="right",
        height=1,
        width=5
    )
    avg_label = Component(
        template="avg",
        justify="right",
        height=1,
        width=5
    )
    avg_value = Component(
        template="{{avg}}",
        justify="right",
        height=1,
        width=7
    )
    time_label = Component(
        template="time",
        justify="left",
        height=1,
        width=5
    )
    time_value = Component(
        template="{{time}}",
        justify="right",
        height=1,
        width=5
    )
    max_label = Component(
        template="max",
        justify="right",
        height=1,
        width=5
    )
    max_value = Component(
        template="{{max}}",
        justify="right",
        height=1,
        width=7
    )
    elev_label = Component(
        template="elev",
        justify="left",
        height=1,
        width=5
    )
    elev_value = Component(
        template="{{elev}}",
        justify="right",
        height=1,
        width=5
    )
    cal_label = Component(
        template="cal",
        justify="right",
        height=1,
        width=5
    )
    cal_value = Component(
        template="{{cal}}",
        justify="right",
        height=1,
        width=7
    )
    watt_label = Component(
        template="watt",
        justify="left",
        height=1,
        width=5
    )
    watt_value = Component(
        template="{{watt}}",
        justify="right",
        height=1,
        width=5
    )
    hr_label = Component(
        template="hr",
        justify="right",
        height=1,
        width=5
    )
    hr_value = Component(
        template="{{hr}}",
        justify="right",
        height=1,
        width=7
    )
    components = [
        top_row,
        second_row_left_icon, name, second_row_right_icon,
        distance_label, distance_value, avg_label, avg_value,
        time_label, time_value, max_label, max_value,
        elev_label, elev_value, cal_label, cal_value,
        watt_label, watt_value, hr_label, hr_value
    ]
    return components


class StravaLastActivityScene(AbstractScene):
    priority: int = 150
    overwritable = True

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:

        if self.get_client_id() is None:
            return SceneExecuteReturn.error(self,
                                            "Strava not configured. Please specify client_id and client_secret in config/settings.ini within the 'StravaLastActivityScene' section")

        if StravaLastActivityScene.is_initialized() is False:
            return SceneExecuteReturn.error(self, "Strava not initialized.")

        last_executed = self.get_last_executed()
        if self.force_positive_rendering is False and last_executed is not None and last_executed + timedelta(minutes=2) > datetime.now():
            return SceneExecuteReturn.error(self, f"strava not executed to protect rate limit ({last_executed})")

        expire_at = datetime.fromtimestamp(int(self.get_config("expires_at")))

        if expire_at < datetime.now():
            refresh_client = Client()
            token_response = refresh_client.refresh_access_token(client_id=self.get_client_id(),
                                                                 client_secret=self.get_client_secret(),
                                                                 refresh_token=self.get_config('refresh_token'))

            StravaLastActivityScene.store_tokens(token_response['access_token'], token_response['refresh_token'],
                                                 token_response['expires_at'])

        try:
            client = Client(access_token=self.get_config("access_token"), rate_limit_requests=False)
            last_activity_summary = client.get_activities(limit=1).next()
            last_activity = client.get_activity(last_activity_summary.id)
        except Fault as e:
            return SceneExecuteReturn.error(self, "Rate Limits exceeded")
        except Exception as e:
            return SceneExecuteReturn.error(self, f"Some unknown stravalib Exception was raised {e}")

        # last_activity = client.get_activity(15880995968)
        
        # ruhrtour2024 11371875821
        # kurze tour 11638289067
        # geisterclam 11621150796
        # schwimmen 11574662901
        # gewichtstraining 8132100578
        # ebikefahrt 15880995968

        logger.info(f"id: {last_activity.id} - name: {last_activity.name} - type: {last_activity.type} - start_date: {last_activity.start_date} - start_date_local: {last_activity.start_date_local}")

        activity_end_date = last_activity.start_date_local + timedelta(seconds=last_activity.elapsed_time.seconds)
        if self.force_positive_rendering == False and ((datetime.now() - timedelta(hours=24)) < activity_end_date) is False:
            self.store_last_executed(datetime.now())
            msg = f"last strava activity '{last_activity.name}' is to old (start_date: {last_activity.start_date_local})"
            return SceneExecuteReturn.error(self, msg)

        start_date = datetime.now()
        end_date = start_date + timedelta(minutes=120)
        end_date = end_date.replace(minute=0, second=0, microsecond=1)

        message = f"Strava: {last_activity.name} - {last_activity.type}"
        logger.info(message)

        td = last_activity.moving_time
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

        if last_activity.type == "EBikeRide":
            name = f"{last_activity.name} {{67}}"
        else:
            name = last_activity.name

        props = {
            "name": name,
            "dist": f"{int(unithelper.kilometer(last_activity.distance))}km",
            "avg": f"{round(float(unithelper.kilometers_per_hour(last_activity.average_speed)), 1)}kmh",
            "time": f"{hours}h{minutes}m",
            "max": f"{round(float(unithelper.kilometers_per_hour(last_activity.max_speed)), 1)}kmh",
            "elev": f"{int(unithelper.meter(last_activity.total_elevation_gain))}m",
        }

        if last_activity.average_heartrate is not None:
            props["hr"] = f"{int(last_activity.average_heartrate)}bpm"
        else:
            props["hr"] = "-"

        if last_activity.average_watts is not None:
            props["watt"] = f"{int(last_activity.average_watts)}w"
        else:
            props["watt"] = "-"

        if last_activity.calories is not None:
            props["cal"] = f"{int(last_activity.calories)}"
        else:
            props["cal"] = "-"

        components = get_components()

        vbml_client = vesta.VBMLClient()
        chars = vbml_client.compose(components, props)
        vesta.pprint(chars)

        self.store_last_executed(datetime.now())
        return SceneExecuteReturn(f"{self.__class__.__name__}_{last_activity.id}_{last_activity.name}", True, self.priority, self,
                                  start_date, end_date, message, chars)

    def get_client_id(self):
        return self.get_config('client_id')

    def get_client_secret(self):
        return self.get_config('client_secret')

    @staticmethod
    def store_tokens(access_token: str, refresh_token: str, expires_at: int):
        scene = StravaLastActivityScene()
        scene.save_config({"access_token": access_token})
        scene.save_config({"refresh_token": refresh_token})
        scene.save_config({"expires_at": str(expires_at)})

    @staticmethod
    def is_initialized() -> bool:
        if StravaLastActivityScene().get_config("access_token") is None:
            return False

        return True

    # noinspection PyMethodMayBeStatic
    def get_last_executed(self) -> Optional[datetime]:
        string_value = self.get_config('last_executed')
        if string_value is None:
            return None

        datetime_value = datetime.fromisoformat(string_value)
        return datetime_value

    # noinspection PyMethodMayBeStatic
    def store_last_executed(self, last_executed: datetime):
        self.save_config({"last_executed": last_executed.now().isoformat()})
