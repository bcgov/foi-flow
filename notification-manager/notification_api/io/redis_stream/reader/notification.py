"""
Start processing only latest records:
$ python consumer.py consumer1 --start-from $
Start processing all records in the stream from the beginning:
$ python consumer.py consumer1 --start-from 0
"""
import json
import typer
import random
import time
import logging
from enum import Enum
from ..redisstreamdb import streamdb
import os
from notification_api.io.message.processor.notificationprocessor import notificationprocessor
from notification_api.io.redis_stream.reader.readerbase import readerbase
LAST_ID_KEY = "{consumer_id}:lastid"
BLOCK_TIME = 5000
NOTIFICATION_STREAM_KEY = os.getenv("NOTIFICATION_STREAM_KEY")

app = typer.Typer()


class StartFrom(str, Enum):
    beginning = "0"
    latest = "$"




@app.command()
def start(consumer_id: str, start_from: StartFrom = StartFrom.latest):
    rdb = streamdb
    stream = rdb.Stream(NOTIFICATION_STREAM_KEY)
    print("stream connected...")
    last_id = rdb.get(LAST_ID_KEY.format(consumer_id=consumer_id))
    readerbase().log_last_msgid(last_id,start_from)    

    while True:
        logging.info("Reading stream...")
        messages = stream.read(last_id=last_id, block=BLOCK_TIME)
        print("messages: ",messages)
        if messages:
            for message_id, message in messages:
                print(f"processing {message_id}::{message}")
                handlemessage(message_id, message)   
                                            
                # simulate processing
                # time.sleep(random.randint(1, 3)) #TODO : todo: remove!
                last_id = message_id
                rdb.set(LAST_ID_KEY.format(consumer_id=consumer_id), last_id)
                logging.info(f"finished processing {message_id}")
        else:
            logging.debug(f"No new messages after ID: {last_id}")
            print(f"No new messages after ID: {last_id}")


def handlemessage(message_id, message):
    logging.info(f"processing {message_id}::{message}")
    print(f"processing {message_id}::{message}")
    if message is not None:                    
        _message = json.dumps({str(key): str(value) for (key, value) in message.items()})
        _message = _message.replace("b'","'").replace("'",'') 
        try:
            notificationprocessor().handlemessage(json.loads(_message))
        except(Exception) as error: 
            logging.exception(error)
            print("Error in processing message: ",error)
    else:
        logging.info("message is empty")