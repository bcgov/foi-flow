# Publication Service: Event Documentation

This document describes the Event-Driven Architecture (EDA) and payload schemas used by the Publication Service.

## 1. Architecture Overview
All communication between the Publication Service and other microservices (e.g., Workflow Service, Scheduler) occurs via Redis Streams using a standardized JSON envelope.

## 2. Standard Envelope
Every event published or consumed by this service follows the standard envelope structure defined in `internal/events/envelope.go`.

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | `string` (UUID) | Unique identifier for the event. |
| `event_type` | `string` | The dot-notated event type (e.g., `openinfo.publish.requested`). |
| `timestamp` | `string` (RFC3339) | When the event was produced. |
| `schema_version` | `string` | The version of the payload schema (currently `1.0.0`). |
| `correlation_id` | `string` | ID used to track a single request across multiple services. |
| `source` | `string` | The name of the service that produced the event. |
| `payload` | `object` | The event-specific data. |
| `meta` | `object` | System-level bookkeeping (retries, errors). |

### 2.1 Envelope Example
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
  "event_type": "example.event.type",
  "timestamp": "2026-04-23T10:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
  "source": "example-service",
  "payload": {},
  "meta": {
    "retry_count": 0,
    "first_seen_at": "2026-04-23T10:00:00Z"
  }
}
```

## 3. Functional Workflows

### 3.1 Open Information (OI) Publishing
Used for publishing documents to the Open Information portal.

#### `openinfo.publish.requested`
- **Producer:** Workflow Service
- **Consumer:** Publication Service
- **Payload Fields:** `tenant_id`, `source` (S3), `destination` (S3), `axis_request_id`, `description`, `published_date`, `contributor`, `fees`, `applicant_type`.

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
  "event_type": "openinfo.publish.requested",
  "timestamp": "2026-04-23T10:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-123",
  "source": "workflow-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "axis_request_id": "EDU-2024-12345",
    "source": { "bucket": "source-bucket", "prefix": "path/to/doc.pdf" },
    "destination": { "bucket": "dest-bucket", "prefix": "published/doc.pdf" },
    "published_date": "2026-04-23"
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T10:00:00Z" }
}
```

#### `openinfo.publish.completed`
- **Producer:** Publication Service
- **Consumer:** Workflow Service
- **Payload Fields:** `tenant_id`, `request_event_id`.

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d92",
  "event_type": "openinfo.publish.completed",
  "timestamp": "2026-04-23T10:05:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-123",
  "source": "publication-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90"
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T10:05:00Z" }
}
```

### 3.2 Proactive Disclosure (PD) Publishing
Used for publishing documents to the Proactive Disclosure portal.

#### `proactivedisclosure.publish.requested`
- **Producer:** Workflow Service
- **Consumer:** Publication Service
- **Payload Fields:** `tenant_id`, `source` (S3), `destination` (S3), `axis_request_id`, `description`, `published_date`, `proactivedisclosure_category`, `report_period`, `contributor`, `fees`, `applicant_type`, `foiministryrequest_id`, `foirequest_id`, `sitemap_pages`, `additionalfiles`, `openinfo_id`.

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d95",
  "event_type": "proactivedisclosure.publish.requested",
  "timestamp": "2026-04-23T11:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-456",
  "source": "workflow-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "axis_request_id": "PD-2024-56789",
    "description": "Quarterly Financial Report",
    "proactivedisclosure_category": "Finance",
    "report_period": "2024-Q1",
    "foiministryrequest_id": 22318,
    "foirequest_id": 22318,
    "source": { "bucket": "source-bucket", "prefix": "pd/report.pdf" },
    "destination": { "bucket": "dest-bucket", "prefix": "published/pd/report.pdf" },
    "published_date": "2026-04-23",
    "sitemap_pages": "",
    "additionalfiles": [
      {
        "additionalfileid": 67,
        "filename": "s.pdf",
        "s3uripath": "https://example/object.pdf",
        "isactive": true
      }
    ],
    "openinfo_id": 0
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T11:00:00Z" }
}
```

#### `proactivedisclosure.publish.completed`
- **Producer:** Publication Service
- **Consumer:** Workflow Service
- **Payload Fields:** `tenant_id`, `request_event_id`.

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d96",
  "event_type": "proactivedisclosure.publish.completed",
  "timestamp": "2026-04-23T11:05:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-456",
  "source": "publication-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d95"
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T11:05:00Z" }
}
```

### 3.3 Sitemapping (OI & PD)
Used for generating and updating sitemaps for the Open Information and Proactive Disclosure portals.

#### `openinfo.sitemapping.requested`
- **Producer:** Publication Service (Scheduler)
- **Consumer:** Publication Service (Sitemap Consumer)
- **Payload Fields:** `tenant_id`, `publication_id`, `public_url`, `last_modified`, `publication_result_ref`.

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d97",
  "event_type": "openinfo.sitemapping.requested",
  "timestamp": "2026-04-23T12:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-789",
  "source": "publication-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "publication_id": "OI-2024-12345",
    "public_url": "https://openinfo.example.gov.bc.ca/search/details/OI-2024-12345",
    "last_modified": "2026-04-23",
    "publication_result_ref": "pub-res-123"
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T12:00:00Z" }
}
```

#### `openinfo.sitemapping.completed`
- **Producer:** Publication Service (Sitemap Consumer)
- **Consumer:** Publication Service (Outbox) / External Subscribers
- **Payload Fields:** `tenant_id`, `publication_id`, `public_url`, `last_modified`, `sitemap_index_key`, `sitemap_page_key`, `sitemap_page_url`, `result`, `index_updated`, `publication_result_ref`.

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d98",
  "event_type": "openinfo.sitemapping.completed",
  "timestamp": "2026-04-23T12:05:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-789",
  "source": "publication-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "publication_id": "OI-2024-12345",
    "public_url": "https://openinfo.example.gov.bc.ca/search/details/OI-2024-12345",
    "last_modified": "2026-04-23",
    "sitemap_index_key": "sitemaps/openinfo/sitemap.xml",
    "sitemap_page_key": "sitemaps/openinfo/sitemap-1.xml",
    "sitemap_page_url": "https://openinfo.example.gov.bc.ca/sitemaps/sitemap-1.xml",
    "result": "written",
    "index_updated": true,
    "publication_result_ref": "pub-res-123"
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T12:05:00Z" }
}
```

#### `proactivedisclosure.sitemapping.requested`
- **Producer:** Publication Service (Scheduler)
- **Consumer:** Publication Service (Sitemap Consumer)
- **Payload Fields:** `tenant_id`, `publication_id`, `public_url`, `last_modified`, `publication_result_ref`.

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d9a",
  "event_type": "proactivedisclosure.sitemapping.requested",
  "timestamp": "2026-04-23T13:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-pd-789",
  "source": "publication-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "publication_id": "PD-2024-56789",
    "public_url": "https://proactivedisclosure.example.gov.bc.ca/search/details/PD-2024-56789",
    "last_modified": "2026-04-23",
    "publication_result_ref": "pub-res-456"
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T13:00:00Z" }
}
```

#### `proactivedisclosure.sitemapping.completed`
- **Producer:** Publication Service (Sitemap Consumer)
- **Consumer:** Publication Service (Outbox) / External Subscribers
- **Payload Fields:** `tenant_id`, `publication_id`, `public_url`, `last_modified`, `sitemap_index_key`, `sitemap_page_key`, `sitemap_page_url`, `result`, `index_updated`, `publication_result_ref`.

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d9b",
  "event_type": "proactivedisclosure.sitemapping.completed",
  "timestamp": "2026-04-23T13:05:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-pd-789",
  "source": "publication-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "publication_id": "PD-2024-56789",
    "public_url": "https://proactivedisclosure.example.gov.bc.ca/search/details/PD-2024-56789",
    "last_modified": "2026-04-23",
    "sitemap_index_key": "sitemaps/proactivedisclosure/sitemap.xml",
    "sitemap_page_key": "sitemaps/proactivedisclosure/sitemap-1.xml",
    "sitemap_page_url": "https://proactivedisclosure.example.gov.bc.ca/sitemaps/sitemap-1.xml",
    "result": "written",
    "index_updated": true,
    "publication_result_ref": "pub-res-456"
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T13:05:00Z" }
}
```

## 4. Common Definitions

This section describes common data structures used across multiple event types.

### `s3_location`
Used to specify the location of an object in S3-compatible storage.

| Field | Type | Description |
|-------|------|-------------|
| `bucket` | `string` | The name of the S3 bucket. |
| `prefix` | `string` | The key or path to the object within the bucket. |

Example:
```json
{
  "bucket": "my-bucket",
  "prefix": "path/to/document.pdf"
}
```
