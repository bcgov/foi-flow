# Publication Service: Event Documentation

This document describes the Event-Driven Architecture (EDA) and payload schemas used by the Publication Service.

## 1. Architecture Overview
All communication between the Publication Service and other microservices (e.g., Workflow Service, Scheduler) occurs via Redis Streams using a standardized JSON envelope.

## 2. Standard Envelope
Every event published or consumed by this service follows the standard envelope structure defined in `internal/events/envelope.go`.

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | `string` (UUID) | Unique identifier for the event. |
| `event_type` | `string` | The dot-notated event type (e.g., `publication.publish.requested`). |
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

The service uses unified publication event types for Open Information and Proactive Disclosure. The payload `kind` field identifies the business flow:

| `kind` | Meaning |
|--------|---------|
| `openinfo` | Open Information publication flow |
| `proactivedisclosure` | Proactive Disclosure publication flow |

### 3.1 Publishing (OI & PD)
Used for publishing documents to the Open Information or Proactive Disclosure portal. The event-driven publish flow copies artifacts, renders the public HTML index, writes sitemap XML inline, and emits a completion event only after both artifact publication and sitemap writing succeed.

#### `publication.publish.requested`
- **Producer:** Workflow Service
- **Consumer:** Publication Service
- **Payload Fields:** `tenant_id`, `kind`, `source` (S3), `destination` (S3), `axis_request_id`, `description`, `published_date`, `contributor`, `fees`, `applicant_type`, plus Proactive Disclosure fields when `kind` is `proactivedisclosure`.
- **Proactive Disclosure Fields:** `proactivedisclosure_category`, `report_period`, `foiministryrequest_id`, `foirequest_id`, `sitemap_pages`, `additionalfiles`, `openinfo_id`.

**Open Information Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
  "event_type": "publication.publish.requested",
  "timestamp": "2026-04-23T10:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-123",
  "source": "openinfo.workflow.service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "kind": "openinfo",
    "axis_request_id": "EDU-2024-12345",
    "source": { "bucket": "source-bucket", "prefix": "path/to/documents/" },
    "destination": { "bucket": "dest-bucket", "prefix": "openinfo/EDU-2024-12345/" },
    "description": "Open Information release package",
    "published_date": "2026-04-23",
    "contributor": "Ministry of Education",
    "fees": 0,
    "applicant_type": "Public"
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T10:00:00Z" }
}
```

**Proactive Disclosure Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d95",
  "event_type": "publication.publish.requested",
  "timestamp": "2026-04-23T11:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-456",
  "source": "proactivedisclosure.workflow.service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "kind": "proactivedisclosure",
    "axis_request_id": "PD-2024-56789",
    "description": "Quarterly Financial Report",
    "proactivedisclosure_category": "Finance",
    "report_period": "2024-Q1",
    "foiministryrequest_id": 22318,
    "foirequest_id": 22318,
    "source": { "bucket": "source-bucket", "prefix": "pd/report/" },
    "destination": { "bucket": "dest-bucket", "prefix": "proactivedisclosure/PD-2024-56789/" },
    "published_date": "2026-04-23",
    "sitemap_pages": "",
    "additionalfiles": [
      {
        "additionalfileid": 67,
        "filename": "supporting-document.pdf",
        "s3uripath": "https://example/object.pdf",
        "isactive": true
      }
    ],
    "openinfo_id": 0
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T11:00:00Z" }
}
```

#### `publication.publish.completed`
- **Producer:** Publication Service
- **Consumer:** Workflow Service / external subscribers
- **Semantics:** Emitted through the outbox after the publish handler and inline sitemap write both succeed.
- **Payload Fields:** `tenant_id`, `request_event_id`, `correlation_id`, `publication_id`, `public_url`, `html_key`, `sitemap_index_key`, `sitemap_page_key`, `sitemap_page_url`, `sitemap_result`, `sitemap_index_updated`, `kind`, `foiministryrequest_id` (optional), `foirequest_id` (optional).

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d92",
  "event_type": "publication.publish.completed",
  "timestamp": "2026-04-23T10:05:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-123",
  "source": "publication.publish.service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
    "correlation_id": "corr-123",
    "publication_id": "EDU-2024-12345",
    "public_url": "https://openinfo.example.gov.bc.ca/packages/EDU-2024-12345.html",
    "html_key": "openinfo/EDU-2024-12345.html",
    "sitemap_index_key": "openinfopub/sitemap/sitemap_index.xml",
    "sitemap_page_key": "openinfopub/sitemap/sitemap_pages_1.xml",
    "sitemap_page_url": "https://openinfo.example.gov.bc.ca/sitemap_pages_1.xml",
    "sitemap_result": "written",
    "sitemap_index_updated": true,
    "kind": "openinfo",
    "foiministryrequest_id": 22318,
    "foirequest_id": 22318
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T10:05:00Z" }
}
```

### 3.2 Unpublishing (OI & PD)
The unpublish flow removes public repository objects under one published prefix, removes the public URL from sitemap XML, and emits a completion event with operational details.

The Redis/event-driven flow emits `publication.unpublish.completed` after successful processing. The synchronous REST endpoint `POST /publications/unpublish` returns a JSON response but does not publish Redis events.

#### `publication.unpublish.requested`
- **Producer:** Workflow Service
- **Consumer:** Publication Service
- **Payload Fields:** `tenant_id`, `kind`, `publication_id`, `public_url`, `public_repository`, `last_modified`, `foiministryrequest_id` (optional), `foirequest_id` (optional).

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
  "event_type": "publication.unpublish.requested",
  "timestamp": "2026-04-27T10:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-unpub-123",
  "source": "openinfo.workflow.service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "kind": "openinfo",
    "publication_id": "EDU-2024-12345",
    "public_url": "https://example.gov.bc.ca/public/EDU-2024-12345.html",
    "public_repository": {
      "bucket": "public-bucket",
      "prefix": "openinfo/EDU-2024-12345/"
    },
    "last_modified": "2026-04-27",
    "foiministryrequest_id": 22318,
    "foirequest_id": 22318
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-27T10:00:00Z" }
}
```

#### `publication.unpublish.completed`
- **Producer:** Publication Service
- **Consumer:** Workflow Service / external subscribers
- **Semantics:** Emitted through the outbox after object deletion and sitemap removal both succeed.
- **Payload Fields:** `tenant_id`, `publication_id`, `request_event_id`, `status`, `public_repository_bucket`, `public_repository_prefix`, `objects_deleted`, `sitemap_index_key`, `sitemap_page_key`, `sitemap_result`, `kind`, `foiministryrequest_id` (optional), `foirequest_id` (optional).

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d93",
  "event_type": "publication.unpublish.completed",
  "timestamp": "2026-04-27T10:05:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-unpub-123",
  "source": "publication.unpublish.service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "publication_id": "EDU-2024-12345",
    "request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
    "status": "completed",
    "public_repository_bucket": "public-bucket",
    "public_repository_prefix": "openinfo/EDU-2024-12345/",
    "objects_deleted": 4,
    "sitemap_index_key": "openinfopub/sitemap/sitemap_index.xml",
    "sitemap_page_key": "openinfopub/sitemap/sitemap_pages_1.xml",
    "sitemap_result": "removed",
    "kind": "openinfo",
    "foiministryrequest_id": 22318,
    "foirequest_id": 22318
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-27T10:05:00Z" }
}
```

### 3.3 Sitemapping (OI & PD)
Used for standalone sitemap generation and updates for the Open Information and Proactive Disclosure portals. Normal event-driven publishing writes sitemap entries inline and reports sitemap metadata in `publication.publish.completed`; the standalone `publication.sitemapping.*` flow remains available for compatibility and isolated tests.

#### `publication.sitemapping.requested`
- **Producer:** Legacy or isolated sitemap workflow
- **Consumer:** Publication Service standalone sitemap adapter
- **Payload Fields:** `tenant_id`, `kind`, `publication_id`, `public_url`, `last_modified`, `publication_result_ref`, `foiministryrequest_id` (optional), `foirequest_id` (optional).

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d97",
  "event_type": "publication.sitemapping.requested",
  "timestamp": "2026-04-23T12:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-789",
  "source": "publication-service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "kind": "openinfo",
    "publication_id": "OI-2024-12345",
    "public_url": "https://openinfo.example.gov.bc.ca/search/details/OI-2024-12345",
    "last_modified": "2026-04-23",
    "publication_result_ref": "pub-res-123",
    "foiministryrequest_id": 22318,
    "foirequest_id": 22318
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T12:00:00Z" }
}
```

#### `publication.sitemapping.completed`
- **Producer:** Publication Service standalone sitemap adapter
- **Consumer:** External subscribers
- **Payload Fields:** `tenant_id`, `kind`, `publication_id`, `public_url`, `last_modified`, `sitemap_index_key`, `sitemap_page_key`, `sitemap_page_url`, `result`, `index_updated`, `publication_result_ref`, `foiministryrequest_id` (optional), `foirequest_id` (optional).

**Full Example Message:**
```json
{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d98",
  "event_type": "publication.sitemapping.completed",
  "timestamp": "2026-04-23T12:05:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "corr-789",
  "source": "publication.sitemapping.service",
  "payload": {
    "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
    "kind": "openinfo",
    "publication_id": "OI-2024-12345",
    "public_url": "https://openinfo.example.gov.bc.ca/search/details/OI-2024-12345",
    "last_modified": "2026-04-23",
    "sitemap_index_key": "sitemaps/openinfo/sitemap.xml",
    "sitemap_page_key": "sitemaps/openinfo/sitemap-1.xml",
    "sitemap_page_url": "https://openinfo.example.gov.bc.ca/sitemaps/sitemap-1.xml",
    "result": "written",
    "index_updated": true,
    "publication_result_ref": "pub-res-123",
    "foiministryrequest_id": 22318,
    "foirequest_id": 22318
  },
  "meta": { "retry_count": 0, "first_seen_at": "2026-04-23T12:05:00Z" }
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
