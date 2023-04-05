import logging
from pathlib import Path

LOG_PATH = Path(".").parent / "logs" / "runner.log"


class _Logger:
    """Custom logging class."""

    def __init__(self):
        """Set instance attributes."""
        self.logger = logging.getLogger("my_log")
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
        )

        file_handler = logging.FileHandler(LOG_PATH)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)


LOGGER = _Logger().logger
