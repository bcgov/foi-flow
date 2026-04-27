import os
import json
import logging
import redis


class RedisSubscriberService:
    def __init__(self, socketio):
        self.socketio = socketio

        # Config
        self.host = os.getenv("SOCKETIO_REDIS_HOST", "localhost")
        self.port = int(os.getenv("SOCKETIO_REDIS_PORT", 6379))
        self.password = os.getenv("SOCKETIO_REDIS_PASSWORD")
        self.channel = os.getenv("SOCKETIO_REDIS_COMMENT_CHANNEL", "foi-comment")
        self.sleep_time = float(os.getenv("SOCKETIO_REDIS_SLEEP_TIME", 0.1))

        # Redis client
        self.redis = redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=0,
            decode_responses=True,
            health_check_interval=int(os.getenv("SOCKETIO_REDIS_HEALTHCHECK_INTERVAL", 30)),
            socket_connect_timeout=int(os.getenv("SOCKETIO_REDIS_CONNECT_TIMEOUT", 5)),
            retry_on_timeout=True,
            socket_keepalive=True
        )

        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        self.thread = None

    def start(self):
        try:
            # 🔍 Connection check
            self.redis.ping()
            logging.info(f"Connected to Redis at {self.host}:{self.port}")

            logging.info(f"Subscribing to Redis channel: {self.channel}")

            self.pubsub.subscribe(**{self.channel: self._event_handler})
            self.thread = self.pubsub.run_in_thread(
                sleep_time=self.sleep_time,
                daemon=True
            )

            logging.info("Redis subscription started")

        except redis.RedisError as e:
            logging.error(f"Redis connection/subscription error: {e}")

        except Exception as e:
            logging.error(f"Unexpected error starting Redis subscriber: {e}")

    def stop(self):
        if self.thread:
            self.thread.stop()
            logging.info("Redis subscription stopped")

    def _event_handler(self, msg):
        try:
            if not msg or msg.get("type") != "message":
                return

            data = msg.get("data")
            if not data:
                return

            payload = json.loads(data)

            user_id = payload.get("userid")
            if not user_id:
                logging.warning("Missing userid in payload")
                return

            # Emit event
            self.socketio.emit(user_id, payload)

        except json.JSONDecodeError:
            logging.error("Invalid JSON received from Redis")

        except Exception as e:
            logging.error(f"Error processing Redis message: {e}")