"""One Flask app for the API tests that run without a database.

request_api.create_app() configures a single module-level app. Flask refuses to configure it again once it has
handled a request, so every such test module must share it instead of calling create_app() itself."""
from request_api import create_app

_client = None


def shared_test_client():
    global _client
    if _client is None:
        _client = create_app().test_client()
    return _client
