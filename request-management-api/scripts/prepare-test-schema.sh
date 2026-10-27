#!/usr/bin/env bash
# Revision 2d8cf3fb689f adds a foreign key to FOIRequestRecords.recordid, which needs a
# unique recordid. The migration that makes recordid the sole primary key is commented out
# (0a70579734e5; applied manually in deployed environments), so an empty test database
# must have it applied before the remaining migrations run.
set -euo pipefail
service_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
project=$1
image=${UPGRADE_APP_IMAGE:-foi-request-api-upgrade:candidate}
compose=(docker compose --project-name "$project" --env-file "$service_dir/tests/upgrade.env" -f "$service_dir/tests/compose.python-upgrade.yml")
docker run --rm --network "${project}_verification" --env-file "$service_dir/tests/upgrade.env" \
    --entrypoint python "$image" manage.py db upgrade bd62026741e2
"${compose[@]}" exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres -d foi_upgrade_test -c \
    'ALTER TABLE "FOIRequestRecords" DROP CONSTRAINT "FOIRequestRecords_pkey", ADD PRIMARY KEY (recordid);'
