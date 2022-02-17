
import os
from request_api.exceptions import BusinessException, Error

from flask import current_app
import redis
import time
from request_api import socketio
import json
import asyncio
class RedisSubscriberService:
   
    foiredis = redis.from_url(os.getenv('FOI_REQUESTQUEUE_REDISURL'), health_check_interval=int(os.getenv('SOCKETIO_HEALTHCHECK_INTERVAL')), socket_connect_timeout=int(os.getenv('SOCKETIO_CONNECT_TIMEOUT')), retry_on_timeout=True, socket_keepalive=True)
    subscription = foiredis.pubsub(ignore_subscribe_messages=True)
            
    @classmethod
    def register_subscription(cls):        
        try: 
            cls.subscription.subscribe(**{os.getenv('SOCKETIO_COMMENT_TOPIC'): event_handler})
            cls.subscription.run_in_thread(sleep_time=float(os.getenv('SOCKETIO_COMMENT_REDIS_TIMEOUT')), daemon=True)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('FOI request Queue REDIS Error', exception.message))              
    
      
def event_handler(msg):
    if msg and msg.get('type') == 'message':
        data = msg.get('data')
        _pushnotification = json.loads(data)
        socketio.emit(_pushnotification["userid"], _pushnotification)
            
