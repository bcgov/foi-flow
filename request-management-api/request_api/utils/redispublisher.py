
import os
from request_api.exceptions import BusinessException, Error

from flask import current_app
from redis import Redis 
from request_api.utils.redissubscriber import RedisSubscriberService
class RedisPublisherService:

    foirequestqueueredishost = os.getenv('FOI_REQUESTQUEUE_REDISHOST')
    foirequestqueueredisport = os.getenv('FOI_REQUESTQUEUE_REDISPORT')
    foirequestqueueredispassword = os.getenv('FOI_REQUESTQUEUE_REDISPASSWORD')
    foirequestqueueredischannel = os.getenv('FOI_REQUESTQUEUE_REDISCHANNEL')
    foicommentqueueredischannel = os.getenv('SOCKETIO_REDIS_COMMENT_CHANNEL')
         
    foiredis = Redis(host=foirequestqueueredishost, port=foirequestqueueredisport,password=foirequestqueueredispassword)
    
    async def publishrequest(self, message):  
        self.publishtoredischannel(self.foirequestqueueredischannel, message)
            
    def publishcommment(self, message):  
        print('publish message')
        print(message)
        self.publishtoredischannel(self.foicommentqueueredischannel, message)
              
    def publishtoredischannel(self, channel , message):  
        try: 
            if channel == os.getenv('FOI_REQUESTQUEUE_REDISCHANNEL'):
                self.foiredis.publish(channel, message) 
            if channel == os.getenv('SOCKETIO_REDIS_COMMENT_CHANNEL'):
                RedisSubscriberService().foicommentredis.publish(channel, message)               
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('FOI request Queue REDIS Error', exception.message))
  
