"""
Start processing only latest records:
$ python consumer.py consumer1 --start-from $
Start processing all records in the stream from the beginning:
$ python consumer.py consumer1 --start-from 0
"""
import json
import typer
import logging

import logging
from enum import Enum

LAST_ID_KEY = "{consumer_id}:lastid"

class StartFrom(str, Enum):
    beginning = "0"
    latest = "$"

class readerbase:

    def log_last_msgid(self, last_id, start_from):
        if last_id:
            logging.debug(f"Resume from ID: {last_id}")
        else:
            logging.debug(f"Starting from {start_from.name}")
