"""Publication event payload models."""

from dataclasses import asdict, dataclass
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
    published_date: Optional[str] = None
    description: Optional[str] = None
    contributor: Optional[str] = None
    fees: int = 0
    applicant_type: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ProactiveDisclosurePublishRequestedPayload:
    """Payload for proactive disclosure publish requested events."""

    tenant_id: str
    axis_request_id: str
    source: S3Location
    destination: S3Location
    published_date: Optional[str] = None
    description: Optional[str] = None
    proactivedisclosure_category: Optional[str] = None
    report_period: Optional[str] = None
    contributor: Optional[str] = None
    fees: int = 0
    applicant_type: Optional[str] = None

    def to_dict(self):
        return asdict(self)

