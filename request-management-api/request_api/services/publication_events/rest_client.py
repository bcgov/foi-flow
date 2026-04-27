"""REST client for the publication service."""

import os

import requests
from requests.exceptions import HTTPError


class PublicationRestClientError(Exception):
    """Raised when the publication REST API returns an unusable response."""


class PublicationRestClient:
    """Publishes OpenInfo and Proactive Disclosure requests through REST."""

    def __init__(self, base_url=None, timeout=None, http_client=None):
        self.base_url = (base_url or os.getenv("PUBLICATION_API_BASE_URL", "")).rstrip("/")
        self.timeout = timeout or int(os.getenv("PUBLICATION_API_TIMEOUT", "30"))
        self.http_client = http_client or requests

    def publish(self, publication_type, payload):
        if not self.base_url:
            raise ValueError("PUBLICATION_API_BASE_URL is not configured")

        response = self.http_client.post(
            f"{self.base_url}/publications",
            json={
                "publication_type": publication_type,
                "payload": payload,
            },
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except HTTPError as exception:
            status_code = response.status_code
            response_body = (response.text or "").strip()
            message = f"Publication API request failed with HTTP {status_code} for {response.url}"
            if response_body:
                message = f"{message}: {response_body}"
            raise PublicationRestClientError(message) from exception
        return response.json()
