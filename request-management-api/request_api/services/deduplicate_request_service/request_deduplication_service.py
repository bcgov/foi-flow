from .redis_service import RedisService
import hashlib
import logging
import json
from request_api.models.default_method_result import DefaultMethodResult

class RequestDeduplicationService:
    """Validate/deduplicate FOI request received from foirequests webform by caching and checking a hash of the request payload in Redis."""
    
    def __init__(self, request_payload, redis_service = None):
        self.request_payload = request_payload
        self.redis_service = redis_service or RedisService()

    def dedupe_service(self):
        try:
            if self.request_payload is None or self.request_payload == {}:
                logging.info("FOI request dedupe service skipped: empty request payload")
                return False
            logging.info(
                "FOI request dedupe service started | "
                "request_data=%s",
                self.request_payload
            )
            hashed_payload = self._hash_payload()
            duplicate_payload = self.redis_service.find_key(hashed_payload)
            if not duplicate_payload:
                logging.info(
                    "No duplicate FOI request found | "
                    "hash=%s",
                    hashed_payload,
                )
                self.redis_service.add_key(hashed_payload)
                return False
            logging.info(
                "Duplicate FOI request found | "
                "hash=%s",
                hashed_payload
            )
            return True
        except Exception:
            logging.exception("FOI request dedupe service skipped: Error in foi request deduplication process")
            return False
        
    def _hash_payload(self):
        self._normalize_request_data(self.request_payload)
        serialized_data = json.dumps(self.request_payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(serialized_data.encode('utf-8')).hexdigest()
    
    def _normalize_request_data(self, request_data):
        request_data.pop("requestId", None)
        request_data.pop("receivedDateUF", None)