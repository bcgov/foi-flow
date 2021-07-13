
import os
from request_api.exceptions import BusinessException, Error

from flask import current_app

class RedisPublisherService:

    foirequestqueueredishost = os.getenv('FOI_REQUESTQUEUE_REDISHOST')
    foirequestqueueredisport = os.getenv('FOI_REQUESTQUEUE_REDISPORT')
    foirequestqueueredispassword = os.getenv('FOI_REQUESTQUEUE_REDISPASSWORD')
    foirequestqueueredischannel = os.getenv('FOI_REQUESTQUEUE_REDISCHANNEL')
         
    
    async def publishtoredischannel(self,message):  
        try: 
            from redis import Redis
            foiredis = Redis(host=self.foirequestqueueredishost, port=self.foirequestqueueredisport,password=self.foirequestqueueredispassword)     
            foiredis.publish(self.foirequestqueueredischannel, message)            
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('FOI request Queue REDIS Error', exception.message))
