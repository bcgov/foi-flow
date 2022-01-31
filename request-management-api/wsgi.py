
from threading import Thread
import eventlet
#Monkey patch to allow for async actions (aka multiple workers)
eventlet.monkey_patch(socket=True)
from distutils.log import debug


import os
from request_api import create_app, socketio
from flask_socketio import emit
from request_api.auth import AuthHelper
from flask import g, request

@socketio.on('connect')
def connect():
    emit(request.sid, {"message": request.sid+" successfully connected"})
  
@socketio.on('disconnect')
def disconnect():
    emit(request.sid, {"message": request.sid+" successfully disconnected"})
    
@socketio.on_error()
def error_handler(e):
    print('Socket error ', e)  

APP = create_app()
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    if os.getenv("SOCKETIO_MESSAGE_QTYPE") == "REDIS":
        socketio.init_app(APP, async_mode='eventlet',
                      message_queue=os.getenv("FOI_REQUESTQUEUE_REDISURL"),
                      redis_options={'REDIS_OPTIONS'},  
                      path='/api/v1/socket.io')
    else:
        socketio.init_app(APP, async_mode='eventlet', 
                      path='/api/v1/socket.io')
    socketio.run(APP, port=port,host='0.0.0.0', debug=True, log_output=True, use_reloader=False)  
    


    
    
