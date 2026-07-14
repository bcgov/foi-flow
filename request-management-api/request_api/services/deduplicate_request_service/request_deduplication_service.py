from redis_service import RedisService
import hashlib
import logging
import json
from request_api.models.default_method_result import DefaultMethodResult

class RequestDeduplicationService:
    """Validate/deduplicate FOI request received from foirequests webform by pushhing and retrieving hashed request payloads from redis stream"""
    def __init__(self, request_payload, redis_service = None):
        self.request_paylod = request_payload
        self.redis_service = redis_service or RedisService()

    def dedupe_service(self):
        try:
            if self.request_paylod in ({}, None):
                raise Exception
            logging.info(
                "FOI request dedupe service started | ",
                "request_data=%s",
                self.request_paylod
            )
            encrypted_payload = self._hash_payload()
            duplicate_payload = self.redis_service.find_key(encrypted_payload)
            if not duplicate_payload:
                logging.info(
                    "No duplicate FOI request found | ",
                    "hash=%s",
                    encrypted_payload,
                    "request_data=%s",
                    self.request_paylod
                )
                self.redis_service.add_key(encrypted_payload)
                return False
            logging.info(
                "Duplicate FOI request found | "
                "hash=%s",
                encrypted_payload
                "request_data=%s"
                self.request_paylod
            )
            return True
        except Exception as exception:
            logging.exception(
                "Error in foi request deduplication process. Deduplication skipped",
                exception,
            )
            return False
        
    def _hash_payload(self):
        serialized_data = json.dumps(self.request_paylod, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(serialized_data.encode('utf-8')).hexdigest()