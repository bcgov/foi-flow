"""Publication event payload models."""

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class S3Location:
    """S3 location included in publication events."""

    bucket: str
    prefix: str


@dataclass
class OpenInfoPublishRequestedPayload:
    """Payload for open information publish requested events."""

    tenant_id: str
    axis_request_id: str
    source: S3Location
    destination: S3Location
    kind: str = "openinfo"
    published_date: Optional[str] = None
    description: Optional[str] = None
    contributor: Optional[str] = None
    fees: int = 0
    applicant_type: Optional[str] = None
    title: Optional[str] = None
    high_level_subject: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    subject: Optional[str] = None
    foirequest_id: Optional[int] = None
    foiministryrequest_id: Optional[int] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class AdditionalFilePayload:
    """Additional file metadata included in publication events."""

    additionalfileid: int
    filename: str
    s3uripath: str
    isactive: bool


@dataclass
class ProactiveDisclosurePublishRequestedPayload:
    """Payload for proactive disclosure publish requested events."""

    tenant_id: str
    axis_request_id: str
    source: S3Location
    destination: S3Location
    kind: str = "proactivedisclosure"
    published_date: Optional[str] = None
    description: Optional[str] = None
    proactivedisclosure_category: Optional[str] = None
    report_period: Optional[str] = None
    contributor: Optional[str] = None
    fees: Optional[str] = None
    applicant_type: Optional[str] = None
    foiministryrequest_id: Optional[int] = None
    foirequest_id: Optional[int] = None
    sitemap_pages: Optional[str] = None
    additionalfiles: list[AdditionalFilePayload] = field(default_factory=list)
    openinfo_id: Optional[int] = None
    title: Optional[str] = None
    high_level_subject: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    subject: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class UnpublishRequestedPayload:
    """Payload for unpublish requested events (OI and PD)."""

    tenant_id: str
    publication_id: str
    public_url: str
    public_repository: S3Location
    last_modified: str
    foirequest_id: Optional[int] = None
    foiministryrequest_id: Optional[int] = None
    kind: str = "openinfo"

    def to_dict(self):
        return asdict(self)
