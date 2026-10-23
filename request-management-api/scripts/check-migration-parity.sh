#!/usr/bin/env bash
# Compare target startup against a schema created by the recorded local baseline.
set -euo pipefail
service_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
project=$1
evidence=$2
baseline_image=${UPGRADE_BASELINE_IMAGE:-foi-request-api-upgrade:baseline}
candidate_image=${UPGRADE_APP_IMAGE:-foi-request-api-upgrade:candidate}
compose=(docker compose --project-name "$project" --env-file "$service_dir/tests/upgrade.env" -f "$service_dir/tests/compose.python-upgrade.yml")
if ! docker image inspect "$baseline_image" >/dev/null 2>&1; then
    echo 'Schema parity not run: supply UPGRADE_BASELINE_IMAGE with a recorded baseline image.' > "$evidence/schema-parity.log"
    exit 0
fi
"${compose[@]}" exec -T postgres createdb -U postgres foi_upgrade_test_baseline
run_migration() {
    docker run --rm --network "${project}_verification" \
        --env-file "$service_dir/tests/upgrade.env" \
        -e DATABASE_TEST_URL=postgresql://postgres:upgrade-test-only@postgres:5432/foi_upgrade_test_baseline \
        -e DATABASE_TEST_NAME=foi_upgrade_test_baseline \
        --entrypoint python "$1" manage.py db upgrade
}
dump_schema() {
    "${compose[@]}" exec -T postgres pg_dump -U postgres -d foi_upgrade_test_baseline --schema-only --no-owner --no-privileges |
        python3 -c 'import sys; print("".join(line for line in sys.stdin if not line.startswith((chr(92)+"restrict ", chr(92)+"unrestrict "))), end="")'
}
docker image inspect --format '{{.Id}}' "$baseline_image" "$candidate_image" > "$evidence/schema-images.txt"
run_migration "$baseline_image" > "$evidence/migrations-baseline.log" 2>&1
dump_schema > "$evidence/schema-before.sql"
run_migration "$candidate_image" > "$evidence/migrations-candidate.log" 2>&1
dump_schema > "$evidence/schema-after.sql"
cmp "$evidence/schema-before.sql" "$evidence/schema-after.sql"
echo 'PASS: candidate startup preserved the baseline schema.' > "$evidence/schema-parity.log"
