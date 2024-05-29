import random
import string
import uuid
import vesta
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from Repository import Repository
from Helper.RawHelper import RawHelper
from datetime import datetime, timedelta
import configparser
from stravalib import Client


class StravaLastActivityScene(AbstractScene):
    client_id: int = 45087
    client_secret: str = '41b89124d848bd73c143b0300fbae4ed4af6fe21'

    priority: int = 150

    def execute(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        if config['strava']['access_token'] == "none":
            print("strava not initialized")
            return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", False, self.priority, self,
                                      None, None, "strava not initialized", None)

        client = Client(access_token=config['strava']['access_token'])

        last_activity = client.get_activities(limit=1).next()

        #print(f"{last_activity.id} - {last_activity.name} - {last_activity.type} - {last_activity.start_date} - {last_activity.start_date_local}")

        if ((datetime.now() - timedelta(hours=1)) < last_activity.start_date_local) is False:
            print("last strava activity is too old")
            return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", False, self.priority, self,
                                      None, None, "last activity is too old", None)

        start_date = datetime.now()
        end_date = start_date + timedelta(minutes=120)

        message = f"Strava: {last_activity.name} - {last_activity.type}"
        print(message)

        chars = vesta.encode_text(
            message,
            valign="middle",
        )

        return SceneExecuteReturn(f"{self.__class__.__name__}_{last_activity.id}", True, self.priority, self,
                                  start_date, end_date, message, chars)
