#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<'EOF'
Simulate the README flow for OpenInfo publish + sitemap mapping.

Prerequisites:
  - docker compose dependencies are available
  - the API process is running with the README Quick Start environment
  - aws CLI is installed

Usage:
  scripts/simulate-openinfo-sitemap.sh

Useful overrides:
  SKIP_COMPOSE_UP=1         Do not run docker compose up -d
  SKIP_WAIT=1               Do not wait for completed Redis events
  WAIT_TIMEOUT_SECONDS=90   Completion wait timeout
  REQUEST_ID=HTH-2025-52023 OpenInfo request ID / generated HTML name
  RUN_ID=demo-1             S3 source and destination prefix suffix
  S3_ENDPOINT=http://localhost:8333
  S3_PUBLIC_URL=http://localhost:8333
  SITEMAP_BUCKET=foi-published
  SITEMAP_PREFIX=sitemap/
  SERVICE_URL=http://localhost:9085
EOF
}

log() {
  printf '[simulate-openinfo-sitemap] %s\n' "$*"
}

die() {
  printf '[simulate-openinfo-sitemap] error: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required"
}

new_uuid() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr '[:upper:]' '[:lower:]'
    return
  fi

  if [[ -r /proc/sys/kernel/random/uuid ]]; then
    cat /proc/sys/kernel/random/uuid
    return
  fi

  die "uuidgen or /proc/sys/kernel/random/uuid is required"
}

redis_cli() {
  docker compose exec -T redis redis-cli "$@"
}

aws_s3() {
  aws --endpoint-url "$S3_ENDPOINT" "$@"
}

ensure_bucket() {
  local bucket="$1"

  if aws_s3 s3api head-bucket --bucket "$bucket" >/dev/null 2>&1; then
    log "bucket exists: s3://$bucket"
    return
  fi

  log "creating bucket: s3://$bucket"
  aws_s3 s3 mb "s3://$bucket" >/dev/null
}

wait_for_stream_value() {
  local stream="$1"
  local needle="$2"
  local timeout="$3"
  local started
  local now

  started="$(date +%s)"

  while true; do
    if redis_cli --raw XRANGE "$stream" - + | grep -F "$needle" >/dev/null; then
      log "observed $needle on $stream"
      return
    fi

    now="$(date +%s)"
    if (( now - started >= timeout )); then
      die "timed out waiting for $needle on $stream"
    fi

    sleep 2
  done
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

require_cmd docker
require_cmd aws
require_cmd grep

: "${S3_ENDPOINT:=http://localhost:8333}"
: "${S3_PUBLIC_URL:=$S3_ENDPOINT}"
: "${AWS_ACCESS_KEY_ID:=access_key}"
: "${AWS_SECRET_ACCESS_KEY:=secret_key}"
: "${AWS_DEFAULT_REGION:=us-east-1}"
: "${SERVICE_URL:=http://localhost:9085}"
: "${WAIT_TIMEOUT_SECONDS:=90}"

export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION

AWS_CONFIG_FILE_CREATED=""
if [[ -z "${AWS_CONFIG_FILE:-}" ]]; then
  AWS_CONFIG_FILE="$(mktemp)"
  AWS_CONFIG_FILE_CREATED="$AWS_CONFIG_FILE"
  export AWS_CONFIG_FILE
  cat >"$AWS_CONFIG_FILE" <<EOF
[default]
region = $AWS_DEFAULT_REGION
s3 =
    addressing_style = path
EOF
fi

cleanup() {
  if [[ -n "$AWS_CONFIG_FILE_CREATED" ]]; then
    rm -f "$AWS_CONFIG_FILE_CREATED"
  fi
}
trap cleanup EXIT

: "${TENANT_ID:=a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10}"
: "${REQUEST_ID:=HTH-2025-52023}"
: "${RUN_ID:=$(date -u +%Y%m%d%H%M%S)}"
: "${PUBLISHED_DATE:=2026-02-03}"
: "${DESCRIPTION:=A copy of briefing note}"
: "${CONTRIBUTOR:=Ministry of Health}"
: "${FEES:=0}"
: "${APPLICANT_TYPE:=Interest Group}"

: "${SOURCE_BUCKET:=foi-raw}"
: "${SOURCE_PREFIX:=incoming/$RUN_ID/}"
: "${SOURCE_OBJECT:=doc.txt}"
: "${DESTINATION_BUCKET:=foi-published}"
: "${DESTINATION_PREFIX:=out/$RUN_ID/}"
: "${SITEMAP_BUCKET:=$DESTINATION_BUCKET}"
: "${SITEMAP_PREFIX:=sitemap/}"

: "${REDIS_STREAM_REQUESTED:=openinfo.publish.requested}"
: "${REDIS_STREAM_COMPLETED:=openinfo.publish.completed}"
: "${REDIS_STREAM_OI_SITEMAP_REQUESTED:=openinfo.sitemapping.requested}"
: "${REDIS_STREAM_OI_SITEMAP_COMPLETED:=openinfo.sitemapping.completed}"

: "${PUBLISH_EVENT_ID:=$(new_uuid)}"
: "${SITEMAP_EVENT_ID:=$(new_uuid)}"
: "${CORRELATION_ID:=openinfo-demo-$RUN_ID}"
: "${SITEMAP_CORRELATION_ID:=openinfo-sitemap-demo-$RUN_ID}"
: "${PUBLICATION_ID:=$REQUEST_ID:v1}"
: "${PUBLIC_URL:=${S3_PUBLIC_URL%/}/$DESTINATION_BUCKET/$DESTINATION_PREFIX$REQUEST_ID.html}"

if [[ "${SKIP_COMPOSE_UP:-0}" != "1" ]]; then
  log "starting compose dependencies"
  docker compose up -d redis postgres seaweedfs >/dev/null
fi

if command -v curl >/dev/null 2>&1; then
  if curl -fsS "$SERVICE_URL/health" >/dev/null 2>&1; then
    log "service health check passed: $SERVICE_URL/health"
  else
    log "service health check did not pass; continuing because the service may still be starting"
  fi
fi

ensure_bucket "$SOURCE_BUCKET"
ensure_bucket "$DESTINATION_BUCKET"
ensure_bucket "$SITEMAP_BUCKET"

log "seeding source object: s3://$SOURCE_BUCKET/$SOURCE_PREFIX$SOURCE_OBJECT"
printf 'hello from the OpenInfo publish simulation\n' |
  aws_s3 s3 cp - "s3://$SOURCE_BUCKET/$SOURCE_PREFIX$SOURCE_OBJECT" >/dev/null

publish_payload="$(cat <<EOF
{
  "event_id": "$PUBLISH_EVENT_ID",
  "event_type": "openinfo.publish.requested",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "schema_version": "1.0.0",
  "correlation_id": "$CORRELATION_ID",
  "source": "openinfo.enqueue.service",
  "payload": {
    "tenant_id": "$TENANT_ID",
    "axis_request_id": "$REQUEST_ID",
    "description": "$DESCRIPTION",
    "published_date": "$PUBLISHED_DATE",
    "contributor": "$CONTRIBUTOR",
    "fees": $FEES,
    "applicant_type": "$APPLICANT_TYPE",
    "source": {"bucket": "$SOURCE_BUCKET", "prefix": "$SOURCE_PREFIX"},
    "destination": {"bucket": "$DESTINATION_BUCKET", "prefix": "$DESTINATION_PREFIX"}
  },
  "meta": {"retry_count": 0, "first_seen_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
}
EOF
)"

log "publishing OpenInfo request event $PUBLISH_EVENT_ID to $REDIS_STREAM_REQUESTED"
redis_cli XADD "$REDIS_STREAM_REQUESTED" '*' payload "$publish_payload" >/dev/null

if [[ "${SKIP_WAIT:-0}" != "1" ]]; then
  wait_for_stream_value "$REDIS_STREAM_COMPLETED" "$PUBLISH_EVENT_ID" "$WAIT_TIMEOUT_SECONDS"
fi

sitemap_payload="$(cat <<EOF
{
  "event_id": "$SITEMAP_EVENT_ID",
  "event_type": "openinfo.sitemapping.requested",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "schema_version": "1.0.0",
  "correlation_id": "$SITEMAP_CORRELATION_ID",
  "source": "openinfo.workflow.service",
  "payload": {
    "tenant_id": "$TENANT_ID",
    "publication_id": "$PUBLICATION_ID",
    "public_url": "$PUBLIC_URL",
    "last_modified": "$PUBLISHED_DATE",
    "publication_result_ref": "$PUBLISH_EVENT_ID"
  },
  "meta": {"retry_count": 0, "first_seen_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
}
EOF
)"

# log "publishing OpenInfo sitemap event $SITEMAP_EVENT_ID to $REDIS_STREAM_OI_SITEMAP_REQUESTED"
# redis_cli XADD "$REDIS_STREAM_OI_SITEMAP_REQUESTED" '*' payload "$sitemap_payload" >/dev/null

# if [[ "${SKIP_WAIT:-0}" != "1" ]]; then
#   wait_for_stream_value "$REDIS_STREAM_OI_SITEMAP_COMPLETED" "$PUBLICATION_ID" "$WAIT_TIMEOUT_SECONDS"
# fi

# log "published HTML index should be at: s3://$DESTINATION_BUCKET/$DESTINATION_PREFIX$REQUEST_ID.html"
# aws_s3 s3 ls "s3://$DESTINATION_BUCKET/$DESTINATION_PREFIX" || true

# log "sitemap objects under s3://$SITEMAP_BUCKET/$SITEMAP_PREFIX"
# aws_s3 s3 ls "s3://$SITEMAP_BUCKET/$SITEMAP_PREFIX" || true

# log "latest OpenInfo completed events"
# redis_cli --raw XREVRANGE "$REDIS_STREAM_COMPLETED" + - COUNT 5 || true

# log "latest OpenInfo sitemap completed events"
# redis_cli --raw XREVRANGE "$REDIS_STREAM_OI_SITEMAP_COMPLETED" + - COUNT 5 || true
