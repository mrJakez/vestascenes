import configparser
from datetime import datetime
from typing import Union


class ConfigHelper:
    @classmethod
    def is_in_operation_hours(cls, now: datetime) -> Union[dict[str, str], None]:
        config = get_config()
        start_hour = int(config['operation-hours']['start'])
        end_hour = int(config['operation-hours']['end'])

        if now.hour < start_hour:
            return {"message": "Not executed - to early"}

        if now.hour >= end_hour:
            return {"message": "Not executed - to late"}

        return None

    @classmethod
    def is_disabled(cls):
        config = get_config()
        return str2bool(config['main']['disabled'])

    @classmethod
    def get_vboard_read_write_key(cls):
        config = get_config()
        key = config['main']['vboard_read_write_key']

        if key is None or len(key) == 0:
            return None

        return key

    @classmethod
    def set_disabled(cls, new_status: bool):

        config = get_config()
        config['main']['disabled'] = str(new_status)

        with open('settings.ini', 'w') as configfile:
            config.write(configfile)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(['settings.ini', '/config/settings.ini'])
    return config
