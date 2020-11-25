import json
import sys
from pathlib import Path

from debrid.constants import bot_config_file_name


def read_config():
    if Path(bot_config_file_name).is_file():
        with open(bot_config_file_name, 'r') as f:
            bot_data = json.load(f)
            return bot_data
    # if the file is missing we return an empty dictionary
    else:
        return {}


def overwrite_config(new_config):
    with open(bot_config_file_name, 'w+') as f:
        json.dump(new_config, f, indent=4)