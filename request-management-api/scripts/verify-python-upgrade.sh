#!/usr/bin/env bash
set -euo pipefail
service_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
phase=${1:-candidate}
if [ "$#" -gt 0 ]; then shift; fi
case "$phase" in baseline|candidate) ;; *) echo 'Usage: verify-python-upgrade.sh [baseline|candidate]' >&2; exit 2 ;; esac
export UPGRADE_EVIDENCE_DIR=${UPGRADE_EVIDENCE_DIR:-/tmp/request-api-python-upgrade/$phase}
export UPGRADE_APP_IMAGE="foi-request-api-upgrade:$phase"
mkdir -p "$UPGRADE_EVIDENCE_DIR"
if [ "$phase" = baseline ]; then
    # Never overwrite the pre-upgrade image with the modified working tree.
    docker image inspect --format '{{.Id}}' "$UPGRADE_APP_IMAGE" > "$UPGRADE_EVIDENCE_DIR/image-id.txt"
    docker run --rm --network none --entrypoint python "$UPGRADE_APP_IMAGE" --version
    docker run --rm --network none --entrypoint python "$UPGRADE_APP_IMAGE" -m pip check
    echo 'Recorded baseline image inspected; this command does not rerun its historical test suite.'
    exit 0
fi
export UPGRADE_TLS_DIR=${UPGRADE_TLS_DIR:-/tmp/request-api-python-upgrade/tls/$phase}
mkdir -p "$UPGRADE_TLS_DIR"
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj /CN=storage \
    -addext subjectAltName=DNS:storage -keyout "$UPGRADE_TLS_DIR/storage.key" \
    -out "$UPGRADE_TLS_DIR/storage.crt" > "$UPGRADE_EVIDENCE_DIR/tls-generation.log" 2>&1
compose=(docker compose --project-name "foi-python-upgrade-$phase" --env-file "$service_dir/tests/upgrade.env" -f "$service_dir/tests/compose.python-upgrade.yml")
cleanup() { "${compose[@]}" logs --no-color > "$UPGRADE_EVIDENCE_DIR/peers.log" 2>&1; "${compose[@]}" down --remove-orphans; }
trap cleanup EXIT
docker build -f "${UPGRADE_DOCKERFILE:-$service_dir/Dockerfile}" -t "$UPGRADE_APP_IMAGE" "$service_dir" 2>&1 | tee "$UPGRADE_EVIDENCE_DIR/build.log"
"${compose[@]}" build checks
"${compose[@]}" up -d --wait --wait-timeout 90 postgres redis storage
if [ "$phase" = candidate ]; then
    bash "$service_dir/scripts/check-migration-parity.sh" "foi-python-upgrade-$phase" "$UPGRADE_EVIDENCE_DIR"
fi
"${compose[@]}" run --rm checks "$@" 2>&1 | tee "$UPGRADE_EVIDENCE_DIR/checks.log"
