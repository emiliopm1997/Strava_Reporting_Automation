import json

from .utils.path_index import CONFIG_JSON


class Config:
    """Configuration variables."""

    def __init__(self):
        """Set instance attributes."""
        with open(CONFIG_JSON, "r") as f:
            self.__conf_old = json.load(f)

        for k, v in self.__conf_old.items():
            setattr(self, k, v)
