"""Maps database rows to publication payloads."""

import os
import uuid
from datetime import datetime

from request_api.services.publication_events.payloads import (
    AdditionalFilePayload,
    OpenInfoPublishRequestedPayload,
    ProactiveDisclosurePublishRequestedPayload,
    S3Location,
    UnpublishRequestedPayload,
)


class PublicationPathResolver:
    """Resolves publication S3 locations."""

    def __init__(self, tenant_id=None):
        self.tenant_id = tenant_id
        self.default_tenant_id = os.getenv("PUBLICATION_TENANT_ID", "foi-flow")
        self.openinfo_publication_bucket = os.getenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
        self.openinfo_source_bucket_suffix = os.getenv("OPENINFO_SOURCE_BUCKET_SUFFIX", "dev-e")
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

    def build_source(self, row):
        return S3Location(
            bucket=f"{row.get('bcgovcode')}-{self.openinfo_source_bucket_suffix}",
            prefix=f"{row.get('axisrequestid')}/responsepackage/",
        )

    def build_destination(self, row):
        return S3Location(
            bucket=self.openinfo_publication_bucket,
            prefix=f"packages/{row.get('axisrequestid')}/openinfo/",
        )


class OpenInfoPublishRequestedMapper:
    """Maps OI query rows to requested-event payloads."""

    def __init__(self, path_resolver=None):
        self.path_resolver = path_resolver or PublicationPathResolver()

    def map(self, row):
        axis_request_id = row.get("axisrequestid")
        return OpenInfoPublishRequestedPayload(
            tenant_id=self.path_resolver.resolve_tenant_id(row),
            axis_request_id=axis_request_id,
            description=row.get("description"),
            published_date=row.get("published_date"),
            contributor=row.get("contributor"),
            fees=int(row.get("fees") or 0),
            applicant_type=row.get("applicant_type"),
            source=self.path_resolver.build_source(row),
            destination=self.path_resolver.build_destination(row),
            title="FOI Request" + " - " + axis_request_id,
            subject="FOI Request",
            high_level_subject="FOI Request",
            month=datetime.now().strftime("%m"),
            year=datetime.now().strftime("%Y"),
            foiministryrequest_id=row.get("foiministryrequestid"),
            foirequest_id=row.get("foirequestid"),
        )

    @staticmethod
    def correlation_id(row):
        return f"openinfo-publish-{row.get('openinfoid')}"


class ProactiveDisclosurePublishRequestedMapper:
    """Maps PD query rows to requested-event payloads."""

    def __init__(self, path_resolver=None):
        self.path_resolver = path_resolver or PublicationPathResolver()

    @staticmethod
    def _map_additional_files(row):
        items = row.get("additionalfiles") or []
        return [
            AdditionalFilePayload(
                additionalfileid=item.get("additionalfileid"),
                filename=item.get("filename"),
                s3uripath=item.get("s3uripath"),
                isactive=bool(item.get("isactive")),
            )
            for item in items
        ]

    def map(self, row):
        category = row.get("proactivedisclosurecategory")
        ministry = row.get("contributor")
        report_period = row.get("reportperiod")
        return ProactiveDisclosurePublishRequestedPayload(
            tenant_id=self.path_resolver.resolve_tenant_id(row),
            axis_request_id=row.get("axisrequestid"),
            description=self._generate_pd_description(category, ministry, report_period),
            published_date=row.get("published_date"),
            contributor=ministry,
            applicant_type="",
            report_period=report_period,
            foiministryrequest_id=row.get("foiministryrequestid"),
            foirequest_id=row.get("foirequestid"),
            sitemap_pages=row.get("sitemap_pages"),
            additionalfiles=self._map_additional_files(row),
            openinfo_id=row.get("openinfoid"),
            source=self.path_resolver.build_source(row),
            destination=self.path_resolver.build_destination(row),
            title=ministry + " - " + category + " - " + report_period,
            high_level_subject=self._generate_high_level_subject(category),
            month=self._generate_pd_month(report_period.split()),
            year=self._generate_pd_year(report_period.split()),
            subject="",
            proactivedisclosure_category=category
        )
    
    def _generate_pd_description(self, pd_category, ministry, report_period):
        match pd_category:
            case "Direct Award Contracts":
                return f"This document is a summary of directly-awarded contracts for the {ministry} for the time period of {report_period}."
            case "Calendars":
                return f"This document represents the calendars for the {ministry}, for the time period of {report_period}."
            case "Contracts over $10,000":
                return f"This document is a summary of contracts with values over $10,000 CAD for the {ministry} for the time period of {report_period}."
            case "Minister Quarterly Travel Expenses":
                return f"This document represents the Travel Expense report for the Minister of {ministry} for the time period of {report_period}."
            case "Estimates":
                return f"Estimates notes prepared for the Minister."
            case "Transition Binders":
                return f"Transition Binder for {ministry}, prepared for the incoming Minister."
            case "Briefing Notes":
                return f"This document is a summary of Briefing Notes for the {ministry} for the time period of {report_period}."
            case "DM Travel Expenses":
                return f"This document represents the Travel Expense report for the Deputy Minister {ministry} for the time period of {report_period}."
            case _:
                return ""

    def _generate_pd_year(self, report_period_arr):
        if len(report_period_arr) == 1:
            return report_period_arr[0]
        if report_period_arr[0] == "Quarter":
            quarter = report_period_arr[1]
            try:
                current_year, next_year = report_period_arr[2].split("-", 1)
            except ValueError:
                raise ValueError("invalid format")
            if quarter == "4":
                return current_year[:2] + next_year

            return current_year
        else:
            return report_period_arr[1]

    def _generate_pd_month(self, report_period_arr):
        if len(report_period_arr) == 1:
            return ""
        if report_period_arr[0] == "Quarter":
            quarter = report_period_arr[1]
            match quarter:
                case "1":
                    return "4"
                case "2":
                    return "7"
                case "3":
                    return "10"
                case "4":
                    return "1"
                case _:
                    return ""
        else:
            return str(datetime.strptime(report_period_arr[0], "%B").month)
        
    def _generate_high_level_subject(self, pd_category):
        match pd_category:
            case "Direct Award Contracts":
                return "Directly-Awarded Contract"
            case "Calendars":
                return "Calendar"
            case "Contracts over $10,000":
                return "Contracts Over 10,000"
            case "Minister Quarterly Travel Expenses":
                return "Travel Expense"
            case "Estimates":
                return "Estimates Notes"
            case "Transition Binders":
                return "Transition Binder"
            case "Briefing Notes":
                return "Briefing Notes"
            case "DM Travel Expenses":
                return "Travel Expense"
            case _:
                return pd_category

    @staticmethod
    def correlation_id(row):
        return f"proactivedisclosure-publish-{row.get('proactivedisclosureid')}"


class UnpublishRequestedMapper:
    """Maps unpublish DB rows to UnpublishRequestedPayload."""

    def __init__(self, path_resolver=None):
        self.path_resolver = path_resolver or PublicationPathResolver()
        self.public_base_url = os.getenv(
            "PUBLICATION_PUBLIC_BASE_URL",
            "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages",
        ).rstrip("/")

    def map(self, row, publication_type="openinfo"):
        axis_request_id = row.get("axisrequestid")
        return UnpublishRequestedPayload(
            tenant_id=self.path_resolver.resolve_tenant_id(row),
            publication_id=axis_request_id,
            public_url=(
                f"{self.public_base_url}/{axis_request_id}/openinfo/{axis_request_id}.html"
            ),
            public_repository=S3Location(
                bucket=self.path_resolver.openinfo_publication_bucket,
                prefix=f"{publication_type}/{axis_request_id}",
            ),
            last_modified=row.get("publicationdate", ""),
            foirequest_id=row.get("foirequest_id"),
            foiministryrequest_id=row.get("foiministryrequestid"),
            kind=publication_type,
        )

    @staticmethod
    def correlation_id(row, publication_type="openinfo"):
        id_field = "openinfoid" if publication_type == "openinfo" else "proactivedisclosureid"
        return f"{publication_type}-unpublish-{row.get(id_field)}"
