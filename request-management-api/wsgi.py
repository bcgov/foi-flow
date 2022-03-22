
from threading import Thread
import eventlet
#Monkey patch to allow for async actions (aka multiple workers)
eventlet.monkey_patch()
from distutils.log import debug


import os
from request_api import create_app, socketio
from flask_socketio import ConnectionRefusedError
from flask_socketio import emit
from request_api.auth import AuthHelper
from flask import g, request
from request_api.auth import AuthHelper
from request_api.exceptions import BusinessException
from flask import current_app
from request_api.utils.redissubscriber import RedisSubscriberService

@socketio.on('connect')
def connect(message):
    current_app.logger.info('socket connection established for user: ' + ' | sid: '+request.sid)
    # userid = __getauthenticateduserid(message)
    # if userid is not None:
    #     else:
    #     disconnect()
    #     raise ConnectionRefusedError('unauthorized!')

 
@socketio.on('disconnect')
def disconnect():
    current_app.logger.info('socket disconnected for sid: '+request.sid)
    

def __getauthenticateduserid(message):
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
    if os.getenv("SOCKETIO_MESSAGE_QTYPE") == "REDIS":
        RedisSubscriberService().register_subscription()
    socketio.init_app(APP, async_mode='eventlet', 
                      path='/api/v1/socket.io')
    socketio.run(APP, port=port,host='0.0.0.0', log_output=False, use_reloader=False)  
    


    
    
