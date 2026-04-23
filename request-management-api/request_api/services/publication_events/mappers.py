"""Maps database rows to publication payloads."""

import os
import uuid

from request_api.services.publication_events.payloads import (
    OpenInfoPublishRequestedPayload,
    ProactiveDisclosurePublishRequestedPayload,
    S3Location,
)


class PublicationPathResolver:
    """Resolves publication S3 locations."""

    def __init__(self, tenant_id=None):
        self.tenant_id = tenant_id
        self.default_tenant_id = os.getenv("PUBLICATION_TENANT_ID", "foi-flow")
        self.tenant_namespace = uuid.UUID(
            os.getenv("PUBLICATION_TENANT_NAMESPACE", str(uuid.NAMESPACE_DNS))
        )

    def resolve_tenant_id(self, row):
        bcgovcode = row.get("bcgovcode")
        if bcgovcode:
            return str(uuid.uuid5(self.tenant_namespace, f"bcgov:{str(bcgovcode).lower()}"))
        if self.tenant_id:
            return self.tenant_id
        return self.default_tenant_id

    @staticmethod
    def resolve_bucket(bcgovcode):
        env = os.getenv("FLASK_ENV", "production")
        suffix_map = {
            "production": "dev-e",
            "development": "dev-e",
        }
        suffix = suffix_map.get(env, "dev-e")
        return f"{bcgovcode}-{suffix}"

    def build_source(self, row):
        return S3Location(
            bucket=self.resolve_bucket(row.get("bcgovcode")),
            prefix=f"{row.get('axisrequestid')}/openinfo/",
        )

    def build_destination(self, row):
        return S3Location(
            bucket=self.resolve_bucket(row.get("bcgovcode")),
            prefix="openinfo/published/",
        )


class OpenInfoPublishRequestedMapper:
    """Maps OI query rows to requested-event payloads."""

    def __init__(self, path_resolver=None):
        self.path_resolver = path_resolver or PublicationPathResolver()

    def map(self, row):
        return OpenInfoPublishRequestedPayload(
            tenant_id=self.path_resolver.resolve_tenant_id(row),
            axis_request_id=row.get("axisrequestid"),
            description=row.get("description"),
            published_date=row.get("published_date"),
            contributor=row.get("contributor"),
            fees=int(row.get("fees") or 0),
            applicant_type=row.get("applicant_type"),
            source=self.path_resolver.build_source(row),
            destination=self.path_resolver.build_destination(row),
        )

    @staticmethod
    def correlation_id(row):
        return f"openinfo-publish-{row.get('openinfoid')}"


class ProactiveDisclosurePublishRequestedMapper:
    """Maps PD query rows to requested-event payloads."""

    def __init__(self, path_resolver=None):
        self.path_resolver = path_resolver or PublicationPathResolver()

    def map(self, row):
        return ProactiveDisclosurePublishRequestedPayload(
            tenant_id=self.path_resolver.resolve_tenant_id(row),
            axis_request_id=row.get("axisrequestid"),
            description=row.get("description"),
            published_date=row.get("published_date"),
            contributor=row.get("contributor"),
            fees=int(row.get("fees") or 0),
            applicant_type=row.get("applicant_type"),
            proactivedisclosure_category=row.get("proactivedisclosurecategory"),
            report_period=row.get("reportperiod"),
            source=self.path_resolver.build_source(row),
            destination=self.path_resolver.build_destination(row),
        )

    @staticmethod
    def correlation_id(row):
        return f"proactivedisclosure-publish-{row.get('proactivedisclosureid')}"
