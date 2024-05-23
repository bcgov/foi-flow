
import os
from request_api.exceptions import BusinessException

from flask import current_app
import time
from request_api import socketio
import json
import redis
import logging
class RedisSubscriberService:
   
    foicommentredis = redis.from_url(os.getenv('SOCKETIO_REDISURL'), health_check_interval=int(os.getenv('SOCKETIO_REDIS_HEALTHCHECK_INTERVAL')), socket_connect_timeout=int(os.getenv('SOCKETIO_REDIS_CONNECT_TIMEOUT')), retry_on_timeout=True, socket_keepalive=True)
    subscription = foicommentredis.pubsub(ignore_subscribe_messages=True)
            
    @classmethod
    def register_subscription(cls):        
        try: 
            logging.warning("subscription to channel")
            cls.subscription.subscribe(**{os.getenv('SOCKETIO_REDIS_COMMENT_CHANNEL'): event_handler})
            cls.subscription.run_in_thread(sleep_time=float(os.getenv('SOCKETIO_REDIS_SLEEP_TIME')), daemon=True)
        except BusinessException as exception:            
            logging.error("%s,%s" % ('FOI request Queue REDIS Error', exception.message))              

    
def event_handler(msg):
    if msg and msg.get('type') == 'message':
        data = msg.get('data')
        _pushnotification = json.loads(data)
        socketio.emit(_pushnotification["userid"], _pushnotification)
            
