
import os
from request_api.exceptions import BusinessException, Error

from flask import current_app
from redis import Redis 
class RedisPublisherService:

    foirequestqueueredishost = os.getenv('FOI_REQUESTQUEUE_REDISHOST')
    foirequestqueueredisport = os.getenv('FOI_REQUESTQUEUE_REDISPORT')
    foirequestqueueredispassword = os.getenv('FOI_REQUESTQUEUE_REDISPASSWORD')
    foirequestqueueredischannel = os.getenv('FOI_REQUESTQUEUE_REDISCHANNEL')
    foicommentqueueredischannel = os.getenv('SOCKETIO_COMMENT_TOPIC')
         
    foiredis = Redis(host=foirequestqueueredishost, port=foirequestqueueredisport,password=foirequestqueueredispassword)
                   
    async def publishrequest(self, message):  
        self.publishtoredischannel(self.foirequestqueueredischannel, message)
            
    async def publishcommment(self, message):  
        self.publishtoredischannel(self.foicommentqueueredischannel, message)
        
        
    def publishtoredischannel(self, channel , message):  
        try: 
            self.foiredis.publish(channel, message)            
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('FOI request Queue REDIS Error', exception.message))
   