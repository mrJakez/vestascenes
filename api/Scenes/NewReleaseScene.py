import datetime
import random
import uuid

import vesta

from Helper.ConfigHelper import ConfigHelper, get_config
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn


def get_stored_git_hash():
    config = get_config()
    if config.has_section("NewReleaseScene") is False:
        return "-"
    return config['NewReleaseScene']['stored-hash']


def store_git_hash(git_hash: str):
    config = get_config()

    if config.has_section("NewReleaseScene") is False:
        config.add_section('NewReleaseScene')

    config['NewReleaseScene']['stored-hash'] = git_hash
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)


class NewReleaseScene(AbstractScene):
    priority = 300

    def execute(self, vboard) -> SceneExecuteReturn:

        # fetch prev version
        prev_hash = get_stored_git_hash()
        # fetch current version
        current_hash = ConfigHelper.get_git_hash()

        if prev_hash == current_hash:
            return SceneExecuteReturn.error(self, "no new version")

        store_git_hash(current_hash)

        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(minutes=5)
        message = f"new version #{current_hash} installed"
        chars = vesta.encode_text(message, align="center", valign="middle")

        return SceneExecuteReturn(f"{self.__class__.__name__}_{current_hash}", True, self.priority, self,
                                  start_date, end_date, message, chars)
