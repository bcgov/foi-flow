
import os
from flask import current_app
import logging
import redis



class RedisPublisherService:
    def __init__(self):
        self.host = os.getenv("SOCKETIO_REDIS_HOST", "localhost")
        self.port = int(os.getenv("SOCKETIO_REDIS_PORT", 6379))
        self.password = os.getenv("SOCKETIO_REDIS_PASSWORD")

        self.request_channel = os.getenv("FOI_REQUESTQUEUE_REDISCHANNEL")
        self.comment_channel = os.getenv("SOCKETIO_REDIS_COMMENT_CHANNEL")
        self.foirequestqueueredischannel = self.request_channel
        self.foicommentqueueredischannel = self.comment_channel

        self.redis = redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=0,
            decode_responses=True,
            socket_connect_timeout=int(os.getenv("SOCKETIO_REDIS_CONNECT_TIMEOUT", 5)),
            retry_on_timeout=True,
            socket_keepalive=True
        )

    def publish_request(self, message):
        self._publish(self.request_channel, message)

    async def publishrequest(self, message):
        self.publish_request(message)

    def publish_comment(self, message):
        try:
            logging.info(f"Publishing comment: {message}")
            self._publish(self.comment_channel, message)
        except Exception as ex:
            current_app.logger.error(f"Unable to publish comment: {ex}")
            raise

    def publishcommment(self, message):
        self.publish_comment(message)

    def _publish(self, channel, message):
        try:
            if not channel:
                raise ValueError("Redis channel is not configured")

            self.redis.publish(channel, message)

            logging.info(f"Message published to channel: {channel}")

        except redis.RedisError as e:
            current_app.logger.error(f"Redis publish error: {e}")
            raise
