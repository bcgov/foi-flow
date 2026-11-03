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
python payment_sla_backfill_cli.py                      # dry run (default): no writes anywhere
python payment_sla_backfill_cli.py --apply              # insert the missing ACTIVE rows
python payment_sla_backfill_cli.py --apply --include-expired
python payment_sla_backfill_cli.py --apply --ministry-request-id 1234   # canary, repeatable
python payment_sla_backfill_cli.py --report-file out.json --report-csv out.csv --strict
```

The summary is printed; the full per-record report is written to `payment_sla_backfill_<mode>_<time>.json`
(`--report-file`, optional `--report-csv`). It holds Form.io ids only for rows created or planned, never payment
URLs, tokens or emails; treat it as confidential anyway (the ids make up the payment link).

Exit codes: `0` ok, `1` a source (Camunda, DB, n8n) failed, `2` some rows failed to write (rerun is safe),
`3` `--strict` and records need manual review.

## Before cutover

1. Dry run, review `manual_review_required` and the exception list; fix or accept each.
2. Decide on `--include-expired` (recommended: without it a late payment after cutover has no row to close).
3. Check `active_rows_past_deadline_notified_at_next_expiry_run`: rows the expiry job already treats as expired (now > `payment_expiry_date` minus 1 day); those applicants are emailed at the next 13:00 run.
4. `--apply`, then rerun the dry run: `eligible_active_payments_still_missing_active_row` must be 0 and
   `sla_rows_would_be_created` 0.
5. Only then suspend Camunda. Reruns after suspension still work (suspended instances are included).

`database_unpaid_payments_without_camunda_instance` (population B) is informational: unpaid payments in the FOI
database that Camunda holds no instance for. Investigate separately.
