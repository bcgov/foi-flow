# Publication Service

A Go service that consumes publication events from Redis Streams, drives processing through a Postgres state machine, and emits completion events via the Transactional Outbox pattern. A unified pipeline handles both OpenInfo and Proactive Disclosure through a `kind` discriminator in event payloads:

- **Publish** — consumes `publication.publish.requested`, inspects the `kind` field (`"openinfo"` or `"proactivedisclosure"`) to apply kind-specific validation and HTML meta tags, copies S3 artefacts, renders an HTML index, updates sitemap XML, and emits `publication.publish.completed`.
- **Unpublish** — consumes `publication.unpublish.requested`, deletes published artefacts and removes sitemap entries, emits `publication.unpublish.completed`.
- **Sitemap mapping** — consumes `publication.sitemapping.requested` as a standalone adapter for isolated compatibility tests. Normal sitemap writing is called inline by the publish and unpublish flows.

All actions share Postgres (`workflow_request`, `event_outbox`), the outbox publisher, the scheduler, and the S3/HTML rendering infrastructure. A `kind` column (`'openinfo'` | `'pd'` | `'openinfo_sitemap'` | `'pd_sitemap'` | `'openinfo_unpublish'` | `'pd_unpublish'`) discriminates rows.

It also exposes an HTTP surface (`/`, `/health`, `/version`, `/publications`, `/publications/unpublish`) for liveness probes, build-info checks, and synchronous REST publication/unpublication.

## Why This Repo Exists

This started as a standard-library HTTP service template and grew into a baseline for event-driven Go services. It demonstrates:

- a Redis Streams consumer with consumer groups and ACKs
- a Postgres-backed state machine with bounded retries, stuck-row recovery, and a poison-message guard
- an outbox publisher that emits downstream events even when Redis was briefly unavailable
- a real S3-to-S3 prefix copier backed by any S3-compatible endpoint (SeaweedFS locally, AWS S3 in production)
- HTML index generation from FOI metadata using `html/template` with `//go:embed`, uploaded via `PutObject` after each copy
- structured `log/slog` logging and OpenTelemetry traces + metrics
- embedded `goose` migrations applied under a Postgres advisory lock so multiple replicas can start safely
- graceful shutdown across the HTTP server and the five background workers
- package boundaries that let `internal/publication/publish` stay ignorant of Redis and `internal/messaging` stay ignorant of business semantics

The event-flow design lives in `docs/superpowers/specs/2026-04-16-openinfo-publish-event-flow-design.md`. The S3 payload design lives in `docs/superpowers/specs/2026-04-17-artifact-publisher-s3-payload-design.md`.

## Architecture

```text
producer ──► Redis Stream (publication.publish.requested)
                 │
                 ▼
          publish consumer (XREADGROUP)
          kind discriminator in payload
                 │
                 ▼
     workflow_request (Postgres state machine, kind col)
                 │
                 ▼
     handler ──► S3 prefix copy (source → destination)
                 │
                 ▼
       render HTML index → upload {requestID}.html
                 │
                 ▼
            update matching sitemap XML in S3
                 │
                 ▼
          event_outbox (kind-tagged rows)
                 │
                 ▼
     outbox publisher ──► publication.publish.completed

unpublish consumer ◄── publication.unpublish.requested
sitemapping consumer ◄── publication.sitemapping.requested (standalone)
scheduler: re-enqueues due retries (routes by kind), resets stuck rows

```

- `internal/publish` — shared types (`Kind`, `S3Location`, `CopyResult`), interfaces (`Copier`, `Uploader`), state machine constants, error classification, and the kind-aware `Repo`.
- `internal/messaging` — generic `Broker` interface, Redis Streams implementation, parameterized `Consumer` (normalizer + validator injected), `Scheduler` (routes by `kind`), outbox publisher; `ClaimInfo` includes a `Kind` field.
- `internal/publication/publish` — unified validation, normalization, `Service.Handle`, and `NormalizerAdapter`; `kind` field determines OI vs PD behavior.
- `internal/publication/sitemapping` — unified sitemapping event adapter.
- `internal/publication/unpublish` — unified unpublish event adapter.
- `internal/sitemapping` — shared sitemap XML writer, result persistence, and object-store abstractions.
- `internal/htmlindex` — HTML index renderer; owns the embedded `template.html` and `Render(TemplateVariables)`.
- `internal/storage/s3` — AWS SDK v2 wrapper; `Copy` (list + server-side copy) and `Upload` (PutObject).
- `internal/events` — envelope struct, JSON schema, event-type constants.
- `internal/storage/postgres` — pgx pool and embedded `goose` migrations.
- `internal/observability` — `log/slog` setup, OpenTelemetry tracer, HTTP middleware, event metrics.
- `internal/app` — startup orchestration; `app.RunEventFlow` wires the three unified consumers (publish, unpublish, sitemapping), the scheduler, and the outbox publisher.
- `cmd/api` — process entrypoint (build vars + signal handling).

## Quick Start

Bring up the dependencies (Postgres, Redis, SeaweedFS), then run the service:

```bash
docker compose up -d

POSTGRES_URL=postgres://foi:foi@localhost:5432/foi?sslmode=disable \
  S3_ENDPOINT=http://localhost:8333 \
  S3_ACCESS_KEY_ID=access_key \
  S3_SECRET_ACCESS_KEY=secret_key \
  S3_PUBLIC_URL=http://localhost:8333 \
  SITEMAP_BUCKET=foi-published \
  SITEMAP_PREFIX=sitemap/ \
  SITEMAP_PUBLIC_BASE_URL=http://localhost:8888/buckets/sitemap/ \
  go run ./cmd/api
```

`POSTGRES_URL`, `S3_ENDPOINT`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_PUBLIC_URL`, and the sitemap storage settings are required. Redis defaults to `localhost:6379`. The `docker-compose.yml` SeaweedFS service is pre-configured with the `access_key` / `secret_key` credentials from [`dev/seaweedfs/s3.json`](/home/alvesfc/workspace/gitea/publication-service/dev/seaweedfs/s3.json).

`docker-compose.yml` also starts [RedisInsight](https://redis.io/insight/) at <http://localhost:5540> for inspecting streams, consumer groups, and pending entries. Point it at host `redis`, port `6379` (or `host.docker.internal:6379` from the browser if RedisInsight can't reach the compose network).

A single `go run ./cmd/api` process boots everything. There is no separate `cmd/consumer` today — on startup the binary:

1. applies pending migrations,
2. ensures the unified consumer groups exist (`publication-publish` on `publication.publish.requested`, `publication-unpublish` on `publication.unpublish.requested`, `publication-sitemapping` on `publication.sitemapping.requested`),
3. starts the HTTP server on `:9085`,
4. starts the **publish consumer**, **unpublish consumer**, **sitemapping consumer**, **scheduler**, and **outbox publisher** in the background (see `app.RunEventFlow` in `internal/app/eventflow.go`).

All background processes shut down together on `SIGINT`/`SIGTERM`.

Then open:

- `http://localhost:9085/` — `Hello, World!`
- `http://localhost:9085/health` — `{"status":"ok"}`
- `http://localhost:9085/version` — build metadata

## Publishing Through REST

`POST /publications` provides a synchronous path for OpenInfo and Proactive Disclosure publication. It accepts a generic wrapper with `publication_type` and a nested type-specific `payload`, validates the nested payload with the same publish schemas used by the Redis consumers, copies the source artifacts, writes the HTML index, updates the matching sitemap, and returns the generated metadata in the HTTP response.

This REST path does not publish Redis events and does not emit `*.publish.completed` or `*.sitemapping.completed` messages. The Redis consumer flow remains separate.

OpenInfo example:

```bash
curl -sS -X POST http://localhost:9085/publications \
  -H 'Content-Type: application/json' \
  -d '{
    "publication_type": "openinfo",
    "payload": {
      "tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
      "axis_request_id": "HTH-2025-52023",
      "description":     "A copy of briefing note",
      "published_date":  "2026-02-03",
      "contributor":     "Ministry of Health",
      "fees":            0,
      "applicant_type":  "Interest Group",
      "source":          {"bucket": "foi-raw",       "prefix": "incoming/a7d9b2f1/"},
      "destination":     {"bucket": "foi-published", "prefix": "out/a7d9b2f1/"}
    }
  }'
```

Proactive Disclosure example:

```bash
curl -sS -X POST http://localhost:9085/publications \
  -H 'Content-Type: application/json' \
  -d '{
    "publication_type": "proactivedisclosure",
    "payload": {
      "tenant_id":                    "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
      "axis_request_id":              "PD-2026-001",
      "description":                  "Quarterly travel expenses",
      "published_date":               "2026-04-01",
      "contributor":                  "Ministry of Transportation",
      "fees":                         0,
      "applicant_type":               null,
      "proactivedisclosure_category": "Travel Expenses",
      "report_period":                "2026-Q1",
      "source":                       {"bucket": "pd-raw",       "prefix": "in/pd1/"},
      "destination":                  {"bucket": "pd-published", "prefix": "out/pd1/"}
    }
  }'
```

Successful responses include the publication ID, public HTML URL, HTML object key, sitemap index key, sitemap page key, and sitemap result:

```json
{
  "status": "completed",
  "publication_type": "openinfo",
  "publication_id": "HTH-2025-52023",
  "public_url": "http://localhost:8333/foi-published/out/a7d9b2f1/HTH-2025-52023.html",
  "html_key": "out/a7d9b2f1/HTH-2025-52023.html",
  "sitemap_index_key": "openinfopub/sitemap/sitemap_index.xml",
  "sitemap_page_key": "openinfopub/sitemap/sitemap_pages_1.xml",
  "sitemap_result": "written"
}
```

## Unpublishing Through REST

`POST /publications/unpublish` provides a synchronous path for removing a published OpenInfo or Proactive Disclosure artifact. It accepts the same generic wrapper shape as `POST /publications`, validates the nested payload with the unpublish schemas, deletes every object under the supplied public repository prefix, removes the public URL from the matching sitemap, and returns operational details.

This REST path does not publish Redis events and does not emit `*.unpublish.completed` messages. The Redis consumer flow remains separate.

Unpublish removes content in two separate steps:

1. Public repository cleanup deletes every object under `public_repository.bucket` and `public_repository.prefix`. The prefix is normalized by trimming leading/trailing slashes and adding one trailing slash before deletion. For example, `bucket=dev-openinfopub` and `prefix=proactivedisclosure/PD-ECC-2026-047540` deletes objects under `s3://dev-openinfopub/proactivedisclosure/PD-ECC-2026-047540/`.
2. Sitemap cleanup removes the entry whose `<loc>` exactly matches `public_url`. The `publication_id` is used for tracking, idempotency, and response data; it is not used to find the sitemap entry. If the sitemap contains a different URL string, including a different domain, path, or trailing slash, the sitemap result is `already_absent`.

The service does not validate that the `public_url` domain matches `kind`. A `kind=proactivedisclosure` request with an `openinfo.gov.bc.ca` URL still attempts to remove that exact URL from the configured sitemap.

OpenInfo example:

```bash
curl -sS -X POST http://localhost:9085/publications/unpublish \
  -H 'Content-Type: application/json' \
  -d '{
    "publication_type": "openinfo",
    "payload": {
      "tenant_id": "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
      "publication_id": "HTH-2025-52023",
      "public_url": "http://localhost:8333/foi-published/out/a7d9b2f1/HTH-2025-52023.html",
      "public_repository": {
        "bucket": "foi-published",
        "prefix": "out/a7d9b2f1"
      },
      "last_modified": "2026-02-03"
    }
  }'
```

Proactive Disclosure example:

```bash
curl -sS -X POST http://localhost:9085/publications/unpublish \
  -H 'Content-Type: application/json' \
  -d '{
    "publication_type": "proactivedisclosure",
    "payload": {
      "tenant_id": "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
      "publication_id": "PD-2026-001",
      "public_url": "http://localhost:8333/pd-published/out/pd1/PD-2026-001.html",
      "public_repository": {
        "bucket": "pd-published",
        "prefix": "out/pd1"
      },
      "last_modified": "2026-04-01"
    }
  }'
```

Successful responses include the publication ID, public URL, deleted object count, public repository location, sitemap index key, sitemap page key when a page was touched, and sitemap result:

```json
{
  "status": "completed",
  "publication_type": "openinfo",
  "publication_id": "HTH-2025-52023",
  "public_url": "http://localhost:8333/foi-published/out/a7d9b2f1/HTH-2025-52023.html",
  "public_repository_bucket": "foi-published",
  "public_repository_prefix": "out/a7d9b2f1/",
  "objects_deleted": 3,
  "sitemap_index_key": "openinfopub/sitemap/sitemap_index.xml",
  "sitemap_page_key": "openinfopub/sitemap/sitemap_pages_1.xml",
  "sitemap_result": "removed"
}
```

## Feeding the consumer a test event

First, create the source and destination buckets in the local SeaweedFS S3 instance, then seed a test object.

> ⚠️ **Important**
> If your SeaweedFS S3 is configured with `s3.json` (access key/secret), you **must NOT** use `--no-sign-request`.
> That flag sends anonymous requests and will result in `AccessDenied`.

---

### 1. Create buckets (one-time setup)

```bash
aws --endpoint-url http://localhost:8333 \
    s3 mb s3://foi-raw

aws --endpoint-url http://localhost:8333 \
    s3 mb s3://foi-published

```

### 2. Seed a source object

```bash
echo "hello" | aws --endpoint-url http://localhost:8333 \
    s3 cp - s3://foi-raw/incoming/a7d9b2f1/doc.txt

```

### 3. Verify the source object

```bash
aws --endpoint-url http://localhost:8333 \
    s3 ls s3://foi-raw/incoming/a7d9b2f1/
```

### Notes

The AWS CLI must use the same credentials configured in [`dev/seaweedfs/s3.json`](/home/alvesfc/workspace/gitea/publication-service/dev/seaweedfs/s3.json):

```bash
export AWS_ACCESS_KEY_ID=access_key
export AWS_SECRET_ACCESS_KEY=secret_key
export AWS_DEFAULT_REGION=us-east-1

aws configure set default.s3.addressing_style path
```

- If you see AccessDenied, check:
  - You are not using `--no-sign-request`
  - SeaweedFS loaded your `s3.json`
  - The AWS CLI credentials match `dev/seaweedfs/s3.json`

Then publish the event. The consumer reads JSON envelopes from the `payload` field of each Redis Stream entry:

```bash
docker compose exec redis redis-cli XADD publication.publish.requested '*' payload '{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
  "event_type": "publication.publish.requested",
  "timestamp": "2026-04-16T12:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "req-demo-1",
  "source": "openinfo.enqueue.service",
  "payload": {
    "kind":            "openinfo",
    "tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
    "axis_request_id": "HTH-2025-52023",
    "description":     "A copy of briefing note",
    "published_date":  "2026-02-03",
    "contributor":     "Ministry of Health",
    "fees":            0,
    "applicant_type":  "Interest Group",
    "source":          {"bucket": "foi-raw",       "prefix": "incoming/a7d9b2f1/"},
    "destination":     {"bucket": "foi-published", "prefix": "out/a7d9b2f1/"}
  },
  "meta": {"retry_count": 0, "first_seen_at": "2026-04-16T12:00:00Z"}
}'
```

The consumer validates and normalizes the event, runs the S3 prefix copy, renders an HTML index page from the FOI metadata, uploads it as `HTH-2025-52023.html` to the destination prefix, writes the matching sitemap entry, the row in `workflow_request` lands in `state='completed'`, and the outbox publisher emits a matching envelope onto `publication.publish.completed`. The completed event payload includes publication metadata and sitemap metadata.

```bash
docker compose exec redis redis-cli XRANGE publication.publish.completed - +
```

The `source` must be in `SOURCE_ALLOWLIST` (default `openinfo.enqueue.service`) or the validator will reject the message.

#### Proactive Disclosure sample

```bash
docker compose exec redis redis-cli XADD publication.publish.requested '*' payload '{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
  "event_type": "publication.publish.requested",
  "timestamp": "2026-04-21T12:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "pd-demo-1",
  "source": "proactivedisclosure.enqueue.service",
  "payload": {
    "kind":                         "proactivedisclosure",
    "tenant_id":                    "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
    "axis_request_id":              "PD-2026-001",
    "description":                  "Quarterly travel expenses",
    "published_date":               "2026-04-01",
    "contributor":                  "Ministry of Transportation",
    "fees":                         0,
    "applicant_type":               null,
    "proactivedisclosure_category": "Travel Expenses",
    "report_period":                "2026-Q1",
    "foiministryrequest_id":        22318,
    "foirequest_id":                22318,
    "source":                       {"bucket": "pd-raw",       "prefix": "in/pd1/"},
    "destination":                  {"bucket": "pd-published", "prefix": "out/pd1/"},
    "sitemap_pages":                "",
    "additionalfiles": [
      {
        "additionalfileid": 67,
        "filename": "s.pdf",
        "s3uripath": "https://example/object.pdf",
        "isactive": true
      }
    ],
    "openinfo_id":                  0
  },
  "meta": {"retry_count": 0, "first_seen_at": "2026-04-21T12:00:00Z"}
}'
```

The publish consumer inspects the `kind` field, copies artefacts from `pd-raw/in/pd1/` to `pd-published/out/pd1/`, renders an HTML index with `proactivedisclosure.category` and `proactivedisclosure.report_period` meta tags, uploads it as `PD-2026-001.html`, writes the matching sitemap entry, and emits a completion event with publication and sitemap metadata onto `publication.publish.completed`:

```bash
docker compose exec redis redis-cli XRANGE publication.publish.completed - +
```

The `source` must be in `SOURCE_ALLOWLIST` or the validator will reject the message. Because the default allowlist only contains `openinfo.enqueue.service`, start the service with both sources:

```bash
SOURCE_ALLOWLIST=openinfo.enqueue.service,proactivedisclosure.enqueue.service
```

#### Sitemap mapping sample

Normal event-driven publishing no longer requires an explicit `*.sitemapping.requested` message. `*.publish.completed` now means both artifact publication and sitemap writing succeeded. Standalone sitemap request adapters remain in the codebase for compatibility and isolated tests, but `app.RunEventFlow` starts a unified sitemapping consumer on `publication.sitemapping.requested`.

```bash
docker compose exec redis redis-cli XADD publication.sitemapping.requested '*' payload '{
  "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d89",
  "event_type": "publication.sitemapping.requested",
  "timestamp": "2026-04-21T12:00:00Z",
  "schema_version": "1.0.0",
  "correlation_id": "pd-demo-10",
  "source": "proactivedisclosure.workflow.service",
  "payload": {
    "kind": "proactivedisclosure",
    "tenant_id": "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
    "publication_id": "PD-2026-001:v1",
    "public_url": "https://example.gov.bc.ca/proactivedisclosurepub/packages/PD-2026-001/openinfo/PD-2026-001.html",
    "last_modified": "2026-04-01",
    "publication_result_ref": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d89"
  },
  "meta": {"retry_count": 0, "first_seen_at": "2026-04-21T12:00:00Z"}
}'
```

### Run with Docker

> ⚠️ **Important**
> The container does **not** inherit the S3 settings from `docker-compose.yml`.
> Pass `S3_ENDPOINT`, `S3_ACCESS_KEY_ID`, and `S3_SECRET_ACCESS_KEY` explicitly, and point them at the SeaweedFS gateway started by Compose.

```bash
docker build -t publication-service \
  --build-arg VERSION=$(git describe --tags --always) \
  --build-arg COMMIT=$(git rev-parse --short HEAD) \
  --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) .

docker run --rm -p 9085:9085 \
  --add-host=host.docker.internal:host-gateway \
  -e POSTGRES_URL=postgres://foi:foi@host.docker.internal:5432/foi?sslmode=disable \
  -e REDIS_ADDR=host.docker.internal:6379 \
  -e S3_ENDPOINT=http://host.docker.internal:8333 \
  -e S3_ACCESS_KEY_ID=access_key \
  -e S3_SECRET_ACCESS_KEY=secret_key \
  -e S3_PUBLIC_URL=http://host.docker.internal:8333 \
  -e SITEMAP_BUCKET=foi-published \
  -e SITEMAP_PREFIX=sitemap/ \
  -e SITEMAP_PUBLIC_BASE_URL=https://example.gov.bc.ca/sitemap/ \
  publication-service
```

If `host.docker.internal` is already available in your Docker environment, you can omit `--add-host=host.docker.internal:host-gateway`.

The build args are surfaced by `GET /version` via `-ldflags "-X main.version=..."`.

## Configuration

Read once at startup from the environment.

### Service

| Variable | Default | Description |
| --- | --- | --- |
| `PORT` | `9085` | HTTP server port |
| `SERVICE_NAME` | `publication-service` | Logical service name used in logs and traces |
| `ENVIRONMENT` | `dev` | Deployment environment (`dev`, `staging`, `prod`, …) |
| `LOG_LEVEL` | `INFO` | Structured log level (`DEBUG`, `INFO`, `WARN`, `ERROR`) |

### Storage

| Variable | Default | Description |
| --- | --- | --- |
| `POSTGRES_URL` | _required_ | pgx-compatible DSN; migrations run on startup |

### Redis Streams

| Variable | Default | Description |
| --- | --- | --- |
| `REDIS_ADDR` | `localhost:6379` | Redis address |
| `REDIS_PASSWORD` | _empty_ | Optional password |
| `REDIS_TLS` | `false` | Enable TLS to Redis |
| `REDIS_STREAM_PUBLISH_REQUESTED` | `publication.publish.requested` | Publish inbound stream |
| `REDIS_STREAM_PUBLISH_COMPLETED` | `publication.publish.completed` | Publish outbound stream (outbox target) |
| `REDIS_PUBLISH_CONSUMER_GROUP` | `publication-publish` | Publish consumer group |
| `REDIS_PUBLISH_CONSUMER_NAME` | hostname or PID | Per-replica publish consumer identity |
| `REDIS_STREAM_SITEMAP_REQUESTED` | `publication.sitemapping.requested` | Sitemapping inbound stream (standalone adapter) |
| `REDIS_STREAM_SITEMAP_COMPLETED` | `publication.sitemapping.completed` | Sitemapping outbound stream |
| `REDIS_SITEMAP_CONSUMER_GROUP` | `publication-sitemapping` | Sitemapping consumer group |
| `REDIS_SITEMAP_CONSUMER_NAME` | `sitemap-worker-1` | Per-replica sitemapping consumer identity |
| `REDIS_STREAM_UNPUBLISH_REQUESTED` | `publication.unpublish.requested` | Unpublish inbound stream |
| `REDIS_STREAM_UNPUBLISH_COMPLETED` | `publication.unpublish.completed` | Unpublish outbound stream |
| `REDIS_UNPUBLISH_CONSUMER_GROUP` | `publication-unpublish` | Unpublish consumer group |
| `REDIS_UNPUBLISH_CONSUMER_NAME` | `unpublish-worker-1` | Per-replica unpublish consumer identity |
| `STREAM_MAXLEN` | `100000` | Approximate cap for `XADD MAXLEN ~` |
| `STREAM_TRIM_INTERVAL` | `1h` | Periodic `XTRIM` cadence |

### Event-flow tuning

| Variable | Default | Description |
| --- | --- | --- |
| `CONSUMER_WORKERS` | `1` | Concurrent worker count |
| `MAX_IN_FLIGHT_EVENTS` | `64` | Backpressure ceiling |
| `HANDLER_TIMEOUT` | `30s` | Per-event handler timeout |
| `RETRY_MAX_ATTEMPTS` | `5` | Bounded retries before dead-lettering |
| `POISON_REPEAT_THRESHOLD` | `3` | Repeat-error count that shortcuts to `dead` |
| `SCHEDULER_INTERVAL` | `5s` | Re-enqueue / stuck-reset poll cadence |
| `STUCK_TIMEOUT` | `2m` | Age after which an in-flight row is reset |
| `OUTBOX_INTERVAL` | `1s` | Outbox publisher poll cadence |
| `SOURCE_ALLOWLIST` | `openinfo.enqueue.service` | Comma-separated `source` values accepted by the validator |
| `UNPUBLISH_SOURCE_ALLOWLIST` | `openinfo.workflow.service,proactivedisclosure.workflow.service` | Comma-separated `source` values accepted by unpublish validators |

### S3

| Variable | Default | Description |
| --- | --- | --- |
| `S3_ENDPOINT` | _required_ | S3-compatible endpoint URL (e.g. `http://localhost:8333` for SeaweedFS, or leave blank for AWS) |
| `S3_ACCESS_KEY_ID` | _required_ | Access key |
| `S3_SECRET_ACCESS_KEY` | _required_ | Secret key |
| `S3_PUBLIC_URL` | _required_ | Public-facing base URL used to build links in the HTML index (e.g. `http://localhost:8333` locally, your CDN origin in production) |
| `S3_REGION` | `us-east-1` | AWS region (used for request signing) |
| `S3_USE_PATH_STYLE` | `true` | Path-style requests — required for SeaweedFS and most non-AWS endpoints |
| `S3_REQUEST_TIMEOUT` | `30s` | Per-request timeout for list, copy, and upload operations |

### Sitemap

| Variable | Default | Description |
| --- | --- | --- |
| `SITEMAP_BUCKET` | _required_ | Bucket containing sitemap XML |
| `SITEMAP_PREFIX` | _required_ | Key prefix for sitemap XML, ending in `/` |
| `SITEMAP_PUBLIC_BASE_URL` | _required_ | Public URL prefix for sitemap page files |
| `SITEMAP_PAGE_LIMIT` | `50000` | Maximum URLs per sitemap page before rollover |
| `SITEMAP_SOURCE_ALLOWLIST` | `openinfo.workflow.service,proactivedisclosure.workflow.service` | Comma-separated `source` values accepted by sitemap validators |

### Build metadata

Injected at build time via linker flags:

```bash
go build -ldflags "-X main.version=v1.2.3 -X main.commit=abc123 -X main.buildDate=2026-04-15T00:00:00Z" ./cmd/api
```

Defaults to `dev` / `unknown` / `unknown`.

## Development

Run the unit tests:

```bash
go test ./...
```

Integration tests use Testcontainers to spin up real Postgres, Redis, and SeaweedFS instances; Docker must be available locally.

Run integration tests:

```bash
go test -tags=integration ./...
```

Format:

```bash
gofmt -w ./cmd ./internal
```

## Example Responses

`GET /`

```text
Hello, World!
```

`GET /health`

```json
{"status":"ok"}
```

`GET /version`

```json
{"version":"v1.2.3","commit":"abc123","buildDate":"2026-04-15T00:00:00Z"}
```

## Extending The Service

Stay along the existing boundaries:

- new env vars → `internal/config`
- new HTTP endpoints → `internal/http/handlers`, registered in `internal/http/server`
- new event types → `internal/events` plus a sibling package under `internal/publication/<action>/`
- new producers reuse `messaging.Outbox` and `messaging.Scheduler` without rewiring transport
- the S3 copy logic lives in `internal/storage/s3`; swap it for another `publish.Copier` implementation without touching the consumer loop

When the binary outgrows a single process, the package layout already permits splitting into `cmd/consumer`, `cmd/scheduler`, and `cmd/publisher` without rewiring the domain code.
