# Payment SLA backfill runbook

Creates the `foi-payment-sla` rows (an **n8n Data Table**, not an FOI database table) for payments that Camunda is
still waiting on, so n8n can expire them and close them after cutover. Run it **before** Camunda is suspended.

Code: `request-management-api/payment_sla_backfill_cli.py`, `request_api/services/paymentslabackfillservice.py`.
Tests: `request-management-api/tests/services/test_payment_sla_backfill.py`.

## What it does

1. **Camunda** (REST): every `foi-fee-processing` instance, whether it waits at `Gateway_1771ld6`, and a whitelist
   of variables (`formId`, `submissionId`, `paymentExpiryDate`, `expirycounter`, `ministryRequestID`, ...). Camunda
   also holds credentials as variables; they are never requested.
2. **FOI database** (read only, `SET TRANSACTION READ ONLY`): the payment must still be unpaid (same rule as
   `FOIRequestPayment.getactivepayment`) and the Form.io ids in its `paymenturl` must equal the Camunda ids.
3. **n8n Data Table** (public API): existing rows, so a rerun never duplicates, resets a deadline or revives a
   closed row.

| Situation | Result |
|---|---|
| Waiting, not yet expired in Camunda (`expirycounter` = 0) | insert `ACTIVE`, `payment_expiry_date` = `paymentExpiryDate`, `expires_at` = end of that date in America/Vancouver (same rule as `Build Payment SLA`; no 20-day fallback). The expiry job decides on `payment_expiry_date` (from one day before it onwards), `expires_at` is only its fallback. `next_state_name` and `metadata.foiRequestMetaData` are copied from Camunda's `foiRequestMetaData`, so a later PAID can post `foi-iao-complete` |
| Already expired and notified in Camunda (`expirycounter` >= 1) | reported; with `--include-expired` an `EXPIRED` row is inserted so a late PAID/CANCELLED still finds it. Never `ACTIVE`: the n8n expiry job would email the applicant a second time |
| Valid row for the same payment already present | kept untouched |
| Terminal (`PAID`/`CANCELLED`/`EXPIRED`) or `PENDING` row for the same payment, or an open row for a different payment | conflict, reported, not touched |
| Paid/cancelled in the FOI DB or Camunda, offline payment, not waiting, stale duplicate instance | skipped with a reason |
| Missing/invalid `formId`/`submissionId`, ids not in the DB payment URL, missing/invalid/disagreeing expiry date | reported for manual review, nothing guessed |
| Several instances for one payment | one row; the others are listed as duplicates |

No schema change, no `wfengine` dependency, no Camunda or n8n workflow change. Backfilled rows are marked by
`comments` starting `BACKFILL(camunda) run <id>` and `metadata.source = camunda-backfill`.

## Configuration (environment, nothing hardcoded)

`BPM_ENGINE_REST_URL`, `BPM_TOKEN_URL`, `BPM_CLIENT_ID`, `BPM_CLIENT_SECRET` (Camunda), `DATABASE_*` (FOI DB),
`N8N_BASE_URL`, `N8N_API_KEY` (n8n public API key), optional `N8N_PAYMENT_SLA_TABLE_ID` (otherwise found by name).

## Commands (run from `request-management-api`)

```bash
python payment_sla_backfill_cli.py --report-csv review.csv       # dry run (default): no writes anywhere
python payment_sla_backfill_cli.py --apply --confirm-plan <plan hash>
python payment_sla_backfill_cli.py --apply --confirm-plan <plan hash> --include-expired
python payment_sla_backfill_cli.py --apply --confirm-plan <plan hash> --ministry-request-id 1234   # canary, repeatable
python payment_sla_backfill_cli.py --report-file out.json --report-csv out.csv --strict
```

The summary is printed; the full per-record report is written to `payment_sla_backfill_<mode>_<time>.json`
(`--report-file`, optional `--report-csv`, a UTF-8 CSV that opens directly in Excel). It holds Form.io ids only for
rows created or planned, never payment URLs, tokens or emails; treat it as confidential anyway (the ids make up the
payment link).

### Review, then apply the same plan

The dry run prints a **plan hash**: a fingerprint of the rows it would write (instance, request, Form.io ids,
status, deadline). `--apply` is refused without `--confirm-plan <hash>`, and it writes nothing if the plan is no
longer the one with that hash (for example a payment was paid, or a new instance appeared, after you reviewed the
CSV). The refused run prints and saves the new plan; review it and confirm its hash. Use the same options
(`--include-expired`, `--ministry-request-id`) in the dry run and in the apply, or the hash will not match.

Exit codes: `0` ok, `1` a source (Camunda, DB, n8n) failed, `2` some rows failed to write (rerun is safe),
`3` `--strict` and records need manual review, `4` the plan changed since the reviewed dry run (nothing written).

## Endpoints (optional, admin only)

The same service is available over HTTP while `PAYMENT_SLA_BACKFILL_ENABLED=true` (default off; turn it off again
after cutover). Both calls need a FOI admin token, `N8N_BASE_URL` and `N8N_API_KEY` in the API's environment, and are
logged with the caller's user id. There is no revert call yet: remove the rows by their `BACKFILL(camunda) run <id>`
comment.

| Call | Body | Result |
|---|---|---|
| `POST /api/foiworkflow/payment-sla-backfill/dry-run` | `{"include_expired": false, "ministry_request_ids": []}` | JSON `{status, plan_hash, report}`; with `?format=csv` a CSV download (UTF-8 BOM, plan hash in the `X-Plan-Hash` header). Writes nothing. |
| `POST /api/foiworkflow/payment-sla-backfill/apply` | the dry-run body plus `"plan_hash"` | Writes the reviewed plan. `409` with the new plan hash (nothing written) if the plan changed; `502` if Camunda, the database or n8n failed. |

Responses are `Cache-Control: no-store`. A full run reads every Camunda instance, so measure it on the target
environment first; if it can exceed the route timeout, use the CLI instead.

## Running it in DEV

Run the CLI from a throwaway pod cloned from the API deployment, which has the same image and environment
(`BPM_*`, `DATABASE_*`) as the API: `oc debug deployment/<request-management-api>`. Set `N8N_BASE_URL` (the in-cluster
URL of DEV n8n) and `N8N_API_KEY` in that shell only. Write the reports to `/tmp` and copy them out before leaving
(`oc cp <debug-pod>:/tmp/review.csv .`).

## Before cutover

1. Dry run, review `manual_review_required` and the exception list; fix or accept each.
2. Decide on `--include-expired` (recommended: without it a late payment after cutover has no row to close).
3. Check `active_rows_past_deadline_notified_at_next_expiry_run`: rows the expiry job already treats as expired (now > `payment_expiry_date` minus 1 day); those applicants are emailed at the next 13:00 run.
4. `--apply --confirm-plan <plan hash of the reviewed dry run>`, then rerun the dry run:
   `eligible_active_payments_still_missing_active_row` must be 0 and
   `sla_rows_would_be_created` 0.
5. Only then suspend Camunda. Reruns after suspension still work (suspended instances are included).

`database_unpaid_payments_without_camunda_instance` (population B) is informational: unpaid payments in the FOI
database that Camunda holds no instance for. Investigate separately.
