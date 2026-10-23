# Request Management API Python upgrade validation

Status: Python 3.13 candidate implemented; DEV smoke test and normal release/security review remain pending. The focused checks and full legacy suite are reported separately. No image has been published or deployed.

## Implementation

Target branch: `FOIMOD-4901_request-api-python313`. Implementation was developed in `.worktrees/request-api-python313` on `feat/request-api-python313`.
Baseline source: `e24fb26f8faca72b130ebf1ed029b17c940c0712`.
Deployed image/interpreter/configuration inventory: not established by local checks.

- Production and local images target Python 3.13.17 Bookworm, pinned to index digest `sha256:a3799099b64fd333f262768c7a64733f6e4edb7bc569813710a100214bdcf278`.
- `requirements.in` records direct inputs. Runtime/test requirements carry exact pins and official PyPI release artifact hashes; both image builds enforce hash checking. The generated lock includes transitive dependencies.
- SBC and Flask-OpenTracing are removed. `request_api/tracer.py` owns the existing decorator using the already direct Jaeger/OpenTracing dependencies. It preserves `Tracer.get_instance().trace()`, the existing service name, sampler/reporter settings and `registries-trace-id` propagation. Tests check request/error spans, parent context, response identity and scope cleanup with both removed packages absent.
- Flask/ORM/auth/serialization dependencies were upgraded together. SQLAlchemy 2 compatibility edits change `case()` arguments, named result-row access and scalar ID extraction while retaining SQL expressions, selected fields and versioning behavior. Marshmallow stays on major version 3.
- Flask-Script was replaced by a supported FlaskGroup/Migrate CLI. `python manage.py db upgrade`, `db current`, `db heads` and `list_routes` remain available. Unused removed-standard-library imports were deleted.
- Socket.IO now explicitly refuses missing/non-object connect credentials instead of swallowing an attribute error. Existing nonce and token paths remain otherwise unchanged.
- The entrypoint uses `exec` for the server so SIGTERM reaches it. Existing migration-before-server ordering remains.
- Native PDF libraries/fonts are installed. The available Expat security update is installed: `libexpat1` and `libexpat1-dev` 2.5.0-1+deb12u5.
- A separate CI workflow runs the focused compatibility suite without registry/deployment credentials. Existing publishing and deployment behavior is unchanged; repository branch protection must make this check required if desired.

## Repeatable verification

Run from the worktree root:

```bash
# Inspect the recorded pre-upgrade image; never rebuild it from modified source.
bash request-management-api/scripts/verify-python-upgrade.sh baseline
# Focused compatibility gate used by CI.
bash request-management-api/scripts/verify-python-upgrade.sh candidate @tests/python-upgrade-focused.txt
# Full legacy suite: preserve its failures and collection errors.
bash request-management-api/scripts/verify-python-upgrade.sh candidate
```

The runner uses disposable PostgreSQL/Redis/storage on an internal Docker network, fake `tests/upgrade.env` credentials, no root application `.env`, no published peer ports and no existing database volumes. A guard runs before imports or migrations, requires PYTHON_DOTENV_DISABLED=1, and validates the actual OSS_S3_HOST and stream host. A sentinel test exercises the real configuration loader without ingesting a local .env. HTTP fixtures refuse unregistered external calls. Cleanup affects only the dedicated Compose project.

The runner also requires OpenSSL to generate an ephemeral storage-only TLS certificate under `/tmp/request-api-python-upgrade/tls/candidate`. The private test key stays outside uploaded evidence; the storage/check containers mount it read-only. The actual application HTTPS upload/signing path and upgraded S3 SDK perform a real disposable bucket upload/readback with byte and content-type checks.

Evidence defaults to `/tmp/request-api-python-upgrade/candidate`: runtime/package inventory, pip consistency/inspection, JUnit XML, build/check logs, baseline/candidate migration logs and canonical schema exports. Reports contain synthetic data only. Generated experiment/audit artifacts are under `/tmp/request-api-python-upgrade`; they are not committed.

Schema comparison uses the recorded local `foi-request-api-upgrade:baseline` image, or `UPGRADE_BASELINE_IMAGE` when supplied. It creates a disposable baseline database, applies the old image's migrations, then runs target migration startup against that same schema. The canonical before/after dumps matched. On a machine without a recorded baseline, this check explicitly reports that parity was not run; it is not a parity pass.

## Evidence and limits

- All 57 initial focused checks passed on the real Python 3.13.17 image, including JWT verification, request read/validation, commits/rollback/version history, real Redis streams, Eventlet Socket.IO/reconnect/Redis notification, native receipt rendering with identical uploaded bytes, storage failure, CDOGS payload, GL-code CLI, migration CLI and actual server startup/SIGTERM.
- Review fixes add default-enabled WSGI background startup, a bounded Eventlet scheduler/consumer integration using real DB records and Redis acknowledgement, dotenv-isolation regressions, and the real S3 roundtrip. The worker integration uses the real publication handler/version writer; its API/workflow section-update leaf is isolated by a test dependency that retains the real DB status update. It does not establish that unchanged API/email/workflow orchestration succeeds in DEV.
- The expanded focused selection also includes existing auth/search/cache/identity/OCR/scheduler checks. The final focused gate passes 118 cases with two explicitly deselected baseline-stale assertions; its evidence is in `/tmp/request-api-python-upgrade/focused-reviewed/`. Do not infer that the whole legacy suite is green.
- Two old scheduler tests are explicitly deselected in the focused argument file: `test_getopeninforecordsforprepublishing_filters_publishable_rows` and `test_getpdrecordsforprepublishing_filters_publishable_rows`. They assert `processingstatus IS NULL` SQL, while baseline source already filters `processingmessage`; the upgrade does not change those predicates. Their result-row doubles were adapted to the SQLAlchemy 2 row interface without changing their expected business outputs or SQL assertions.
- The original suite has a collection error in `tests/services/test_publication_completed_consumer.py`, importing four obsolete consumer class names. Other failures involve legacy asyncio assumptions, fixtures and integration expectations. The [full-suite comparison](python-upgrade-test-comparison.md) records 157 baseline passes/76 failures/one collection error versus 230 candidate passes/70 failures/one collection error after review fixes. No previously passing baseline test newly failed; six previously failing cases passed. The final comparison retains the same methodology and preserves every remaining failure by name. No business assertions are weakened to obtain a green gate.
- Normal/large-file production configurations, deployed identity/storage endpoints, resource thresholds and release rollback artifacts still require the existing DEV/TEST/PROD process. Local mocks do not establish deployed integration compatibility.

## Security findings

The dependency audit found no-fix advisories for `python-jose` (asymmetric/HMAC key confusion) and its `ecdsa` dependency (signing side channels). Runtime usage of python-jose is unverified claim parsing, while REST cryptographic verification uses flask-jwt-oidc 0.9/PyJWT with RS256. The focused auth suite rejects expired/wrong-signature/wrong-issuer/wrong-audience tokens and a manually forged HS256 token signed with DER public-key bytes. No ECDSA signing is used. This is an applicability assessment, not blanket library clearance; unchanged socket-token validation behavior remains part of existing security review.

The initial host-venv audit also reported its pip 25.3. Actual candidate image pip is 26.2.2, so that host-tool finding is not a runtime image result.

Grype scanned the full Debian/native image archive. The preliminary scan contained many inherited Bookworm package findings, including 144 unique High/Critical advisory IDs (package/advisory matches are more numerous). Available High/Critical fixes were the Expat packages above and were applied. Other findings were reported without available fixes or with distro-specific dispositions. The post-fix scan retained inherited OS findings but no High/Critical package with a published fix; this is not vulnerability clearance. The scanned image config is `sha256:2acdc4add0ed9e95d264a430bd35d4c632f026f8cd32e6557e734ea0609b5cf2`; the later review build shares its first 11 of 13 immutable layers, including all OS and installed-dependency layers (proof: `/tmp/request-api-python-upgrade/image-layer-proof.json`). Remaining layer differences are application/test/document source and its entrypoint file permissions. Preserve the scan and its image identity and use the normal security review process to assess applicability/acceptance. The image is not asserted vulnerability-free; a slim-image or distro redesign is outside this change.

## DEV handoff checklist

The user performs the DEV smoke test through the existing deployment process. Record the tested source revision and image digest, effective configuration reference and previous immutable image before a release.

- Confirm runtime, successful migration startup, `/api/healthz` and `/api/readyz`.
- Check login, permitted/denied roles and representative request create/view/update/search behavior.
- Check notifications, Socket.IO reconnect, publication completion and retry/recovery.
- Generate/download HTML and CDOGS receipts and verify contents/layout/storage.
- Review startup, authentication, database, storage and background-processing logs against baseline.
- Record pass/failure details and affected synthetic records. Do not reset streams or replay whole queues during rollback.

DEV acceptance requires the user's result. TEST/PROD completion still requires their existing release validation/approvals. Reverting an image does not undo completed DB, S3 or Redis effects.

Both production and local Dockerfiles built successfully; the local image also passed pip consistency checks. Workflow validation with actionlint and shell syntax checks passed. Superpowers planning documents are excluded from the implementation commit.
