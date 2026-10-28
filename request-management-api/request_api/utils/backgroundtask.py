"""Fire-and-forget work that runs after a request without sharing its DB session."""
import contextvars
import logging

import eventlet
from flask import copy_current_request_context, current_app, has_request_context

logger = logging.getLogger(__name__)


def runinbackground(func, *args, **kwargs):
    """Run func(*args, **kwargs) in its own greenlet and Flask app context.

    The greenlet gets a fresh app context, and therefore its own db.session and
    connection, so the caller's teardown can never roll back a connection the
    task is still using. The request context is copied when present because
    some tasks read the caller's token from request.headers.
    """
    if has_request_context():
        target = copy_current_request_context(func)
    else:
        app = current_app._get_current_object()

        def target(*targs, **tkwargs):
            with app.app_context():
                return func(*targs, **tkwargs)

    def run():
        try:
            # An empty Context guarantees Flask pushes a new app context instead of reusing the caller's.
            contextvars.Context().run(target, *args, **kwargs)
        except Exception:
            logger.exception("Background task %s failed", getattr(func, "__qualname__", func))

    return eventlet.spawn(run)
