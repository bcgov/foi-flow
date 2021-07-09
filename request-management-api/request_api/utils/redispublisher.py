import redis
import os
from request_api.exceptions import BusinessException, Error
from flask import current_app

class RedisPublisherService:

    foirequestqueueredishost = os.getenv('FOI_REQUESTQUEUE_REDISHOST')
    foirequestqueueredisport = os.getenv('FOI_REQUESTQUEUE_REDISPORT')
    foirequestqueueredispassword = os.getenv('FOI_REQUESTQUEUE_REDISPASSWORD')
    foirequestqueueredischannel = os.getenv('FOI_REQUESTQUEUE_REDISCHANNEL')
        
    foiredis = redis.Redis(host=foirequestqueueredishost, port=foirequestqueueredisport,password=foirequestqueueredispassword)

    async def publishtoredischannel(self,message):  
        try:      
            self.foiredis.publish(self.foirequestqueueredischannel, message)            
        except BusinessException as exception:
            current_app.logger.error("%s,%s" % ('FOI request Queue REDIS Error', exception.message))
