import json
from copy import deepcopy

import pandas as pd

from .utils.log import LOGGER
from .utils.path_index import CONFIG_JSON, CONFIG_JSON_OLD


class Config:
    """Configuration variables."""

    def __init__(self):
        """Set instance attributes."""
        with open(CONFIG_JSON, "r") as f:
            self.__conf_old = json.load(f)

        for k, v in self.__conf_old.items():
            setattr(self, k, v)

    def save(self):
        """Save the updated config."""
        self.last_updated = str(pd.Timestamp.now(tz="America/Mexico_City"))

        LOGGER.info("Saving old config...")
        with open(CONFIG_JSON_OLD, "w") as outfile:
            json.dump(self.__conf_old, outfile)

        config_new = deepcopy(self.__dict__)
        config_new.pop("_Config__conf_old")
        LOGGER.info("Saving new config...")
        with open(CONFIG_JSON, "w") as outfile:
            json.dump(config_new, outfile)
