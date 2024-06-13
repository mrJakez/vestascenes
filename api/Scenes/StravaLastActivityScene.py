import random
import string
import uuid
import vesta
from vesta.vbml import Component
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

        expire_at = datetime.fromtimestamp(int(config['strava']['expires_at']))

        if expire_at < datetime.now():
            print("strava expire => refresh right now")
            refresh_client = Client()
            token_response = refresh_client.refresh_access_token(client_id=self.client_id,
                                                                 client_secret=self.client_secret,
                                                                 refresh_token=config['strava']['refresh_token'])
            print(f"token_response: {token_response}")
            StravaLastActivityScene.store_tokens(token_response['access_token'], token_response['refresh_token'],
                                                 token_response['expires_at'])
            config.read('config.ini')

        client = Client(access_token=config['strava']['access_token'])
        #last_activity = client.get_activities(limit=1).next()
        last_activity = client.get_activity(11371875821)

        print(
            f"{last_activity.id} - {last_activity.name} - {last_activity.type} - {last_activity.start_date} - {last_activity.start_date_local}")

        #if ((datetime.now() - timedelta(hours=1)) < last_activity.start_date_local) is False:
        #    print("last strava activity is too old")
        #    return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", False, self.priority, self,
        #                              None, None, "last activity is too old", None)

        start_date = datetime.now()
        end_date = start_date + timedelta(minutes=120)

        message = f"Strava: {last_activity.name} - {last_activity.type}"
        print(message)

        #        chars = vesta.encode_text(
        #            message,
        #           valign="middle",
        #        )




        top_left_icon = Component(
            "{63}{63}",
            justify="center",
            align="top",
            height=1,
            width=2
        )

        main_text = Component(
            "Vestaboard Markup Language",
            justify="center",
            align="bottom",
            width=22,
            height=1
        )

        components = [top_left_icon, main_text]

        vbml_client = vesta.VBMLClient()
        chars = vbml_client.compose(components)
        vesta.pprint(chars)

        #return SceneExecuteReturn(f"{self.__class__.__name__}_{last_activity.id}", True, self.priority, self, start_date, end_date, message, chars)
        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self,
                                  start_date, end_date, message, chars)

    @staticmethod
    def store_tokens(access_token: str, refresh_token: str, expires_at: int):
        config = configparser.ConfigParser()
        config.read('config.ini')

        config['strava']['access_token'] = access_token
        config['strava']['refresh_token'] = refresh_token
        config['strava']['expires_at'] = str(expires_at)

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
