import logging
import os
import threading
import time

import requests

"""
Low-level client for the Form.io API, logging in as a limited Form.io user (FOIMOD-5525).
Settings are read on each call; nothing happens at import. Tokens, passwords, response bodies
and submission data are never logged and never put in exception messages.
"""

logger = logging.getLogger(__name__)

TIMEOUT = (10, 10)
# The token is not decoded (RMA cannot verify Form.io's signature). It is reused for a fixed
# time, shorter than Form.io's token lifetime; an earlier expiry is handled by one re-login.
_TOKEN_TTL = 900
_FORM_ID_TTL = 3600
_EXPIRED_SESSION_STATUSES = (401, 440)

_TOKEN = {"value": None, "exp": 0.0}
_FORM_IDS = {}  # form name -> (id, cached_at)
_LOCK = threading.Lock()


class FormioNotConfigured(Exception):
    pass


class FormioError(Exception):
    pass


class FormioNotFound(FormioError):
    pass


def _now():
    return time.time()


def reset_cache():
    with _LOCK:
        _TOKEN["value"] = None
        _TOKEN["exp"] = 0.0
        _FORM_IDS.clear()


class formioservice:

    def _setting(self, name):
        value = os.getenv(name)
        if value is None or not value.strip():
            raise FormioNotConfigured(f"{name} is not configured")
        return value

    def _baseurl(self):
        return self._setting("FORMIO_URL").rstrip("/")

    def _login(self):
        """Log in and cache the token. The caller must hold _LOCK."""
        baseurl = self._baseurl()
        email = self._setting("FORMIO_PAYMENT_USER_EMAIL")
        password = self._setting("FORMIO_PAYMENT_USER_PASSWORD")
        try:
            response = requests.post(
                f"{baseurl}/user/login",
                json={"data": {"email": email, "password": password}},
                timeout=TIMEOUT,
            )
        except requests.RequestException:
            raise FormioError("Form.io unreachable") from None
        if response.status_code >= 400:
            raise FormioError(f"Form.io login returned {response.status_code}")
        token = response.headers.get("x-jwt-token")
        if not token:
            raise FormioError("Form.io login returned no token")
        _TOKEN["value"] = token
        _TOKEN["exp"] = _now() + _TOKEN_TTL
        return token

    def _gettoken(self, stale=None):
        """Return a valid token, logging in if needed. `stale` is a token the server just refused."""
        with _LOCK:
            token = _TOKEN["value"]
            if token is None or token == stale or _now() >= _TOKEN["exp"]:
                token = self._login()
            return token

    def _send(self, method, path, token, **kwargs):
        headers = dict(kwargs.pop("headers", None) or {})
        headers["x-jwt-token"] = token
        try:
            return requests.request(
                method, f"{self._baseurl()}{path}", headers=headers, timeout=TIMEOUT, **kwargs
            )
        except requests.RequestException:
            raise FormioError("Form.io unreachable") from None

    def _request(self, method, path, **kwargs):
        token = self._gettoken()
        response = self._send(method, path, token, **kwargs)
        if response.status_code in _EXPIRED_SESSION_STATUSES:
            token = self._gettoken(stale=token)
            response = self._send(method, path, token, **kwargs)
        if response.status_code == 404:
            raise FormioNotFound("Form.io returned 404")
        if response.status_code >= 400:
            raise FormioError(f"Form.io {method} returned {response.status_code}")
        return response

    def _json(self, response, *required):
        """Parse a JSON object response; anything else becomes a FormioError without the body."""
        try:
            body = response.json()
            if not isinstance(body, dict) or any(key not in body for key in required):
                raise ValueError
        except ValueError:
            raise FormioError("Form.io returned an unexpected response") from None
        return body

    def getformid(self, formname):
        """Return the Form.io id of a form by its path name, cached for an hour."""
        with _LOCK:
            cached = _FORM_IDS.get(formname)
            if cached and _now() - cached[1] < _FORM_ID_TTL:
                return cached[0]
        formid = self._json(self._request("GET", f"/{formname}"), "_id")["_id"]
        with _LOCK:
            _FORM_IDS[formname] = (formid, _now())
        return formid

    def createsubmission(self, formid, data):
        response = self._json(
            self._request("POST", f"/form/{formid}/submission", json={"data": data}), "_id", "form"
        )
        return {"formId": response["form"], "submissionId": response["_id"]}

    def getsubmission(self, formid, submissionid):
        return self._json(self._request("GET", f"/form/{formid}/submission/{submissionid}"))

    def patchsubmission(self, formid, submissionid, fields):
        operations = [{"op": "replace", "path": f"/data/{k}", "value": str(v)} for k, v in fields.items()]
        self._request("PATCH", f"/form/{formid}/submission/{submissionid}", json=operations)
