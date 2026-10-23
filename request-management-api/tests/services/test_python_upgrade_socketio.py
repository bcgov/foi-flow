"""Run the existing Eventlet socket handlers and real Redis subscriber together."""

import subprocess
import sys
from pathlib import Path

from test_python_upgrade_startup import synthetic_environment


def test_socket_authorization_reconnect_and_redis_notification():
    script = '''
import os
os.environ['SOCKETIO_CONNECT_NONCE'] = 'upgrade-socket-only'
from wsgi import APP, socketio
from request_api.utils.redissubscriber import RedisSubscriberService
import redis
import json
import time
socketio.init_app(APP, async_mode='eventlet', path='/api/v1/socket.io')
rejected = socketio.test_client(APP, auth={})
assert not rejected.is_connected()
auth = {'userid': 'upgrade-user', 'rkey': 'upgrade-socket-only'}
client = socketio.test_client(APP, auth=auth)
assert client.is_connected()
client.disconnect()
client = socketio.test_client(APP, auth=auth)
assert client.is_connected()
subscriber = RedisSubscriberService(socketio)
subscriber.start()
broker = redis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
deadline = time.monotonic() + 5
while broker.pubsub_numsub(subscriber.channel)[0][1] < 1:
    assert time.monotonic() < deadline, 'subscriber did not become ready'
    time.sleep(0.02)
payload = {'userid': 'upgrade-user', 'message': 'upgrade-check'}
broker.publish(subscriber.channel, json.dumps(payload))
received = []
while not received and time.monotonic() < deadline:
    time.sleep(0.02)
    received = client.get_received()
assert received == [{'name': 'upgrade-user', 'args': [payload], 'namespace': '/'}], received
client.disconnect()
subscriber.stop()
subscriber.pubsub.close()
broker.close()
'''
    result = subprocess.run(
        [sys.executable, '-c', script], cwd=Path(__file__).resolve().parents[2],
        env=synthetic_environment(), capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
