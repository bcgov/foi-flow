#!/usr/bin/env bash
# Run only the normal Go unit suite. No integration tag or service credentials.
set -euo pipefail

report_dir=${1:?Usage: publication-unit-tests.sh REPORT_DIRECTORY}
mkdir -p "$report_dir"
report_dir=$(cd "$report_dir" && pwd)
if [[ -n "$(find "$report_dir" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo 'Use an empty report directory so stale evidence cannot pass validation.' >&2
  exit 1
fi
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$repo_root/publication-service"

# Do not inherit a developer's build tags or automatically change toolchains.
export GOENV=off
export GOTOOLCHAIN=local
export GOFLAGS=-mod=readonly
go_version=$(go env GOVERSION)
declared_go_version=$(awk '$1 == "go" { print $2 }' go.mod | tr -d '\r')
if [[ "$go_version" != go1.25.0 || "$declared_go_version" != 1.25.0 ]]; then
  echo 'This unit workflow requires the declared Go 1.25.0 toolchain.' >&2
  exit 1
fi
commit_sha=$(git -c safe.directory="$repo_root" -C "$repo_root" rev-parse HEAD)
if [[ -n "${GITHUB_SHA:-}" && "$GITHUB_SHA" != "$commit_sha" ]]; then
  echo 'The checkout SHA differs from GITHUB_SHA; refusing mislabeled results.' >&2
  exit 1
fi
goos=$(go env GOOS)
goarch=$(go env GOARCH)
started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
started_seconds=$(date +%s)

# Capture the exit status explicitly so reports survive a failed test command.
# The final exit preserves that failure; it is never ignored or retried.
if go test -count=1 -timeout=5m -json -coverprofile="$report_dir/coverage.out" ./... \
    > "$report_dir/tests.jsonl" 2> "$report_dir/stderr.log"; then
  test_exit=0
else
  test_exit=$?
fi
duration_seconds=$(( $(date +%s) - started_seconds ))

coverage_text_exit=1
coverage_html_exit=1
if [[ -s "$report_dir/coverage.out" ]]; then
  if go tool cover -func="$report_dir/coverage.out" \
      > "$report_dir/coverage.txt" 2> "$report_dir/coverage-text-stderr.log"; then
    coverage_text_exit=0
  else
    coverage_text_exit=$?
  fi
  if go tool cover -html="$report_dir/coverage.out" -o "$report_dir/coverage.html" \
      2> "$report_dir/coverage-html-stderr.log"; then
    coverage_html_exit=0
  else
    coverage_html_exit=$?
  fi
fi

# These values are fixed command strings, numeric statuses, git hashes and Go
# platform identifiers. PR titles, branch names and other free text are omitted.
printf '{\n  "commit_sha": "%s",\n  "pr_head_sha": "%s",\n  "event_name": "%s",\n  "go_version": "%s",\n  "goos": "%s",\n  "goarch": "%s",\n  "command": "go test -count=1 -timeout=5m -json -coverprofile=REPORT_DIRECTORY/coverage.out ./...",\n  "started_at": "%s",\n  "duration_seconds": %s,\n  "test_exit_code": %s,\n  "coverage_text_exit_code": %s,\n  "coverage_html_exit_code": %s\n}\n' \
  "$commit_sha" "${PR_HEAD_SHA:-}" "${GITHUB_EVENT_NAME:-local}" \
  "$go_version" "$goos" "$goarch" "$started_at" "$duration_seconds" \
  "$test_exit" "$coverage_text_exit" "$coverage_html_exit" > "$report_dir/run.json"

if (( test_exit != 0 )); then
  exit "$test_exit"
fi
if (( coverage_text_exit != 0 || coverage_html_exit != 0 )); then
  echo 'Coverage report generation failed; inspect the saved diagnostics.' >&2
  exit 1
fi
# The separate reporter also rejects zero cases, incomplete JSON and missing
# artifacts. A successful go command alone is deliberately not the final gate.
