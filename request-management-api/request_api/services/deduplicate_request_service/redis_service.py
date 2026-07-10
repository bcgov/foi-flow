import os
import logging
from datetime import datetime
import redis
from request_api.models.default_method_result import DefaultMethodResult
from walrus import Database

REDIS_KEY_TTL_SECONDS = os.getenv("FOIREQUEST_DEDUPE_REDIS_KEY_TTL", 1800)
KEY_PREFIX = "foirequest-dedupe:"

class RedisService:
    """Redis service to connect, store and find keys in foiflow redis"""
    def __init__(self):
        self.host = os.getenv("PUBLICATION_REDIS_HOST", "localhost")
        self.port = int(os.getenv("PUBLICATION_REDIS_PORT", 6379))
        self.password = os.getenv("PUBLICATION_REDIS_PASSWORD")
        self.client = redis.Redis(
            host=self.host,
            port=self.password,
            db=0,
            password=self.password,
            decode_responses=True
        )

    def add_key(self, hashed_payload):
        try:
            logging.info(
                "Adding foirequest-dedupe key to redis | ",
                "redis_key=%s",
                KEY_PREFIX + hashed_payload
            )
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.client.set(KEY_PREFIX + hashed_payload, timestamp, ex=REDIS_KEY_TTL_SECONDS)
            return DefaultMethodResult(True, 'Key added to redis service', KEY_PREFIX + hashed_payload)
        except Exception as exception:
           logging.exception(
               "Error in accessing to Redis",
                exception,
            )
           raise exception

    def find_key(self, hashed_payload):
        try:
            logging.info(
                "Looking for foirequest-dedupe key in redis | "
                "redis_key=%s",
                KEY_PREFIX + hashed_payload
            )
            return self.client.exists(KEY_PREFIX + hashed_payload)
        except Exception as exception:
            logging.exception(
               "Error in accessing to Redis",
                exception,
            )
            raise exception