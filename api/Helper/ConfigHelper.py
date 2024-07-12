from typing import List, Union, Dict
import os, time
from datetime import datetime
import configparser


class ConfigHelper:
    @classmethod
    def is_in_operation_hours(cls, now:datetime) -> Union[dict[str, str], None]:
        config = configparser.ConfigParser()
        config.read('settings.ini')
        start_hour = int(config['operation-hours']['start'])
        end_hour = int(config['operation-hours']['end'])

        if now.hour <= start_hour:
            return {"message": "Not excuted - to early"}

        if now.hour >= end_hour:
            return {"message": "Not excuted - to late"}
        #

        return None


    @classmethod
    def is_disabled(cls):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        return str2bool(config['main']['disabled'])

    @classmethod
    def set_disabled(cls, new_status: bool):

        config = configparser.ConfigParser()
        config.read('settings.ini')
        config['main']['disabled'] = str(new_status)

        with open('settings.ini', 'w') as configfile:
            config.write(configfile)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")