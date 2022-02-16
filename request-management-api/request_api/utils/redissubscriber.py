
import os
from request_api.exceptions import BusinessException, Error

from flask import current_app
from redis import Redis
import time
from request_api import socketio
import json
import asyncio
class RedisSubscriberService:
    
    @classmethod
    def register_subscription(cls):        
        try: 
            foiredis = Redis(host=os.getenv('FOI_REQUESTQUEUE_REDISHOST'), port=os.getenv('FOI_REQUESTQUEUE_REDISPORT'),password=os.getenv('FOI_REQUESTQUEUE_REDISPASSWORD'))    
            subscription = foiredis.pubsub(ignore_subscribe_messages=True)
            subscription.subscribe(**{os.getenv('SOCKETIO_COMMENT_TOPIC'): event_handler})
            subscription.run_in_thread(sleep_time=float(os.getenv('SOCKETIO_COMMENT_REDIS_TIMEOUT')), daemon=True)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('FOI request Queue REDIS Error', exception.message))
    
      
def event_handler(msg):
    if msg and msg.get('type') == 'message':
        data = msg.get('data')
        _pushnotification = json.loads(data)
        socketio.emit(_pushnotification["userid"], _pushnotification)
            
