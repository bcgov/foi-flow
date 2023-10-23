
import os
from request_api.exceptions import BusinessException, Error

from flask import current_app
from redis import Redis 
from request_api.utils.redissubscriber import RedisSubscriberService
import logging
import redis
class RedisPublisherService:

    foirequestqueueredischannel = os.getenv('FOI_REQUESTQUEUE_REDISCHANNEL')
    foicommentqueueredischannel = os.getenv('SOCKETIO_REDIS_COMMENT_CHANNEL')
         
    foimsgredis = redis.from_url(os.getenv('SOCKETIO_REDISURL'), socket_connect_timeout=int(os.getenv('SOCKETIO_REDIS_CONNECT_TIMEOUT')), retry_on_timeout=True, socket_keepalive=True)
    
    async def publishrequest(self, message):  
        self.publishtoredischannel(self.foirequestqueueredischannel, message)
            
    def publishcommment(self, message):  
        try:
            logging.info(message)
            self.publishtoredischannel(self.foicommentqueueredischannel, message)
        except Exception as ex:
            current_app.logger.error("%s,%s" % ('Unable to get user details', ex.message)) 
            raise ex
              
    def publishtoredischannel(self, channel , message):  
        try: 
            if channel == os.getenv('FOI_REQUESTQUEUE_REDISCHANNEL'):
                self.foimsgredis.publish(channel, message) 
            if channel == os.getenv('SOCKETIO_REDIS_COMMENT_CHANNEL'):
                RedisSubscriberService().foicommentredis.publish(channel, message)               
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('FOI request Queue REDIS Error', exception.message))
  
