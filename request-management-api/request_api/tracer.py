# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Service-owned request tracing using the existing Jaeger/OpenTracing backend."""

from functools import wraps

from flask import current_app, request
from jaeger_client import Config
import opentracing
from opentracing.ext import tags
from werkzeug.exceptions import HTTPException


class Tracer:
    """Provide one tracer and the existing resource-handler decorator."""

    __instance = None

    @staticmethod
    def get_instance():
        """Retrieve the service's shared request tracer."""
        if Tracer.__instance is None:
            Tracer()
        return Tracer.__instance

    def __init__(self):
        """Initialize the existing Jaeger configuration once."""
        if Tracer.__instance is not None:
            raise RuntimeError('Attempt made to create multiple tracing instances')

        config = Config(
            # Preserve the existing service name and propagation header.
            service_name='Authentication Services',
            config={
                'sampler': {'type': 'const', 'param': 1},
                'logging': True,
                'reporter_batch_size': 1,
                'trace_id_header': 'registries-trace-id',
            },
        )
        self.tracer = config.initialize_tracer() or opentracing.tracer
        Tracer.__instance = self

    def trace(self, *attributes):
        """Trace a resource call without changing its return value or exceptions."""
        def decorate(handler):
            @wraps(handler)
            def traced(*args, **kwargs):
                headers = {key.lower(): value for key, value in request.headers}
                try:
                    parent = self.tracer.extract(opentracing.Format.HTTP_HEADERS, headers)
                except (opentracing.InvalidCarrierException,
                        opentracing.SpanContextCorruptedException):
                    parent = None

                with self.tracer.start_active_span(
                    request.endpoint or handler.__name__, child_of=parent,
                ) as scope:
                    span = scope.span
                    span.set_tag(tags.COMPONENT, 'Flask')
                    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)
                    span.set_tag(tags.HTTP_METHOD, request.method)
                    span.set_tag(tags.HTTP_URL, request.base_url)
                    for attribute in attributes:
                        value = getattr(request, attribute, None)
                        if value not in (None, '', b''):
                            span.set_tag(attribute, str(value))
                    try:
                        result = handler(*args, **kwargs)
                        span.set_tag(tags.HTTP_STATUS_CODE,
                                     current_app.make_response(result).status_code)
                        return result
                    except Exception as error:
                        span.set_tag(tags.ERROR, True)
                        status = error.code if isinstance(error, HTTPException) else 500
                        span.set_tag(tags.HTTP_STATUS_CODE, status)
                        span.log_kv({'event': tags.ERROR, 'error.object': error})
                        raise

            return traced

        return decorate
