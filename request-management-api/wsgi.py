
from threading import Thread
import os
#Monkey patch to allow for async actions (aka multiple workers)
#Monkey patch only in non-development environments to support dev debugging.
if os.getenv('FLASK_ENV') != "development" :
    import eventlet
    eventlet.monkey_patch()
from distutils.log import debug



from request_api import create_app, socketio
from flask_socketio import ConnectionRefusedError
from flask_socketio import emit
from request_api.auth import AuthHelper
from flask import g, request
from request_api.auth import AuthHelper
from request_api.exceptions import BusinessException
from flask import current_app
from request_api.utils.redissubscriber import RedisSubscriberService
import logging

@socketio.on('connect')
def connect(message):
    userid = __getauthenticateduserid(message)
    if userid is not None:
        current_app.logger.info('socket connection established for user: ' + userid + ' | sid: ' + request.sid)
    else:
        disconnect()
        raise ConnectionRefusedError('unauthorized!')

 
@socketio.on('disconnect')
def disconnect():
    current_app.logger.info('socket disconnected for sid: '+request.sid)
    

def __getauthenticateduserid(message):    
    if message.get("userid") is not None and __isvalidnonce(message) == True: 
        return message.get("userid")
    else:
        return __validatejwt(message)   
      

def __isvalidnonce(message):
    if message.get("rkey") is not None and message.get("rkey") == os.getenv("SOCKETIO_CONNECT_NONCE"):
        return True
    return False

def __validatejwt(message):
    if message.get("x-jwt-token") is not None:
        try:
            return AuthHelper.getwsuserid(message.get("x-jwt-token"))            
        except BusinessException as exception: 
            current_app.logger.error("%s,%s" % ('Unable to get user details', exception.message)) 
    return None 

@socketio.on_error()
def error_handler(e):
    current_app.logger.error("%s,%s" % ('Socket error', e.message))

APP = create_app()
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))    
    messagequeue = os.getenv('SOCKETIO_MESSAGE_QUEUE', 'INMEMORY')
    if os.getenv('FLASK_ENV') != "development" :
        APP.run(host='0.0.0.0',debug=True,port=port)    
    else:
        if os.getenv("SOCKETIO_MESSAGE_QTYPE") == "REDIS":
            RedisSubscriberService().register_subscription()
        socketio.init_app(APP, async_mode='eventlet', 
                      path='/api/v1/socket.io')    
        socketio.run(APP, port=port,host='0.0.0.0', log_output=False, use_reloader=False)  
    


    
    
