import configparser
import os
from datetime import datetime, timedelta
from typing import Optional

import vesta
from stravalib import Client, unithelper
from vesta.vbml import Component

from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn


class StravaLastActivityScene(AbstractScene):
    client_id: int = 130077
    client_secret: str = '6f06db47b8ba9f95ec33a68b42dcb4db32cad8e5'

    priority: int = 150

    def execute(self, vboard) -> SceneExecuteReturn:
        if StravaLastActivityScene.is_initialized() is False:
            return SceneExecuteReturn.error(self, "strava not initialized")

        last_executed = self.get_last_executed()
        if last_executed is not None and last_executed + timedelta(minutes=2) > datetime.now():
            return SceneExecuteReturn.error(self, f"strava not executed to protect rate limit ({last_executed})")

        config = configparser.ConfigParser()
        config.read('/config/strava.ini')
        expire_at = datetime.fromtimestamp(int(config['strava']['expires_at']))

        if expire_at < datetime.now():
            refresh_client = Client()
            token_response = refresh_client.refresh_access_token(client_id=self.client_id,
                                                                 client_secret=self.client_secret,
                                                                 refresh_token=config['strava']['refresh_token'])

            StravaLastActivityScene.store_tokens(token_response['access_token'], token_response['refresh_token'],
                                                 token_response['expires_at'])
            config.read('/config/strava.ini')

        client = Client(access_token=config['strava']['access_token'])
        last_activity_summary = client.get_activities(limit=1).next()
        last_activity = client.get_activity(last_activity_summary.id)

        #last_activity = client.get_activity(8132100578)
        #ruhrtour2024 11371875821
        #kurze tour 11638289067
        #geisterclam 11621150796
        #schwimmen 11574662901
        #gewichtstraining 8132100578

        print(
            f"{last_activity.id} - {last_activity.name} - {last_activity.type} - {last_activity.start_date} - {last_activity.start_date_local}")

        activity_end_date = last_activity.start_date_local + timedelta(seconds=last_activity.elapsed_time.seconds)
        if ((datetime.now() - timedelta(hours=24)) < activity_end_date) is False:
            self.store_last_executed(datetime.now())
            msg = f"last strava activity '{last_activity.name}' is to old (start_date: {last_activity.start_date_local})"
            return SceneExecuteReturn.error(self, msg)

        start_date = datetime.now()
        end_date = start_date + timedelta(minutes=120)
        end_date = end_date.replace(minute=0, second=0, microsecond=1)

        message = f"Strava: {last_activity.name} - {last_activity.type}"
        print(message)

        td = last_activity.moving_time
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

        props = {
            "name": last_activity.name,
            "dist": f"{int(unithelper.kilometer(last_activity.distance))}km",
            "avg": f"{int(unithelper.kilometers_per_hour(last_activity.average_speed))}kmh",
            "time": f"{hours}h{minutes}m",
            "max": f"{int(unithelper.kilometers_per_hour(last_activity.max_speed))}kmh",
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

        vbml_client = vesta.VBMLClient()
        chars = vbml_client.compose(components, props)
        vesta.pprint(chars)

        self.store_last_executed(datetime.now())
        return SceneExecuteReturn(f"{self.__class__.__name__}_{last_activity.id}", True, self.priority, self,
                                  start_date, end_date, message, chars)

    @staticmethod
    def store_tokens(access_token: str, refresh_token: str, expires_at: int):
        config = configparser.ConfigParser()

        # delete and read
        config.write(open('/config/strava.ini', 'w'))
        config.read('/config/strava.ini')

        config.add_section("strava")
        config['strava']['access_token'] = access_token
        config['strava']['refresh_token'] = refresh_token
        config['strava']['expires_at'] = str(expires_at)

        with open('/config/strava.ini', 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def is_initialized() -> bool:
        if not os.path.exists('/config/strava.ini'):
            return False

        return True

    # noinspection PyMethodMayBeStatic
    def get_last_executed(self) -> Optional[datetime]:
        config = configparser.ConfigParser()
        config.read('/config/strava.ini')

        if config.has_option('strava', 'last_executed') is False:
            return None

        string_value = config.get('strava', 'last_executed')
        datetime_value = datetime.fromisoformat(string_value)
        return datetime_value

    # noinspection PyMethodMayBeStatic
    def store_last_executed(self, last_executed: datetime):
        config = configparser.ConfigParser()
        config.read('/config/strava.ini')
        config.set('strava', 'last_executed', last_executed.now().isoformat())

        with open('/config/strava.ini', 'w') as configfile:
            config.write(configfile)
