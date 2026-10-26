-- FOIMOD-5453: literal-only validation of the raw receipt projection/filter
-- contract in request_api/models/FOIRawRequests.py. No application rows are read.
-- Run with psql -X -w -v ON_ERROR_STOP=1 -P pager=off -f - against each target
\set ON_ERROR_STOP on
BEGIN TRANSACTION READ ONLY;
SET LOCAL statement_timeout = '15s';
SET LOCAL lock_timeout = '3s';
SET LOCAL idle_in_transaction_session_timeout = '30s';

WITH cases(label, status, created_at, raw, filter_day, expected_date, expected_uf, expected_included) AS (
  VALUES
    ('historical_midnight', 'Unopened', timestamp '2025-01-15 07:30:00', '{}'::json,
     date '2025-01-14', '2025-01-14', '2025-01-14 23:30:00', true),
    ('historical_noon', 'Unopened', timestamp '2025-01-15 20:00:00', '{}'::json,
     date '2025-01-15', '2025-01-15', '2025-01-15 12:00:00', true),
    ('november_before', 'Unopened', timestamp '2026-11-01 08:59:59', '{}'::json,
     date '2026-11-01', '2026-11-01', '2026-11-01 01:59:59', true),
    ('november_after', 'Unopened', timestamp '2026-11-01 09:00:00', '{}'::json,
     date '2026-11-01', '2026-11-01', '2026-11-01 02:00:00', true),
    ('before_local_midnight', 'Unopened', timestamp '2026-11-03 06:59:59', '{}'::json,
     date '2026-11-03', '2026-11-02', '2026-11-02 23:59:59', false),
    ('at_local_midnight', 'Unopened', timestamp '2026-11-03 07:00:00', '{}'::json,
     date '2026-11-03', '2026-11-03', '2026-11-03 00:00:00', true),
    ('local_midnight', 'Unopened', timestamp '2026-11-03 07:30:00', '{}'::json,
     date '2026-11-03', '2026-11-03', '2026-11-03 00:30:00', true),
    ('after_filter_day', 'Unopened', timestamp '2026-11-04 07:00:00', '{}'::json,
     date '2026-11-03', '2026-11-04', '2026-11-04 00:00:00', false),
    ('cutoff_minutes', 'Unopened', timestamp '2026-11-02 23:31:00', '{}'::json,
     date '2026-11-02', '2026-11-02', '2026-11-02 16:31:00', true),
    ('future_winter', 'Unopened', timestamp '2027-01-15 19:00:00', '{}'::json,
     date '2027-01-15', '2027-01-15', '2027-01-15 12:00:00', true),
    ('saved_receipt', 'Unopened', timestamp '2026-11-02 23:31:00',
     '{"receivedDate":"2026-11-03","receivedDateUF":"2026-11-03 00:00:00"}'::json,
     date '2026-11-03', '2026-11-03', '2026-11-03 00:00:00', true),
    ('saved_date_only', 'Intake in Progress', timestamp '2026-11-02 23:31:00',
     '{"receivedDate":"2025-01-15","receivedDateUF":"2025-01-15"}'::json,
     date '2025-01-15', '2025-01-15', '2025-01-15', true)
), actual AS (
  SELECT *,
    CASE WHEN status = 'Unopened' AND raw -> 'receivedDate' IS NULL
         THEN to_char(timezone('America/Vancouver', timezone('UTC', created_at)), 'YYYY-MM-DD')
         ELSE nullif(raw ->> 'receivedDate', '') END AS actual_date,
    CASE WHEN status = 'Unopened' AND raw -> 'receivedDateUF' IS NULL
         THEN to_char(timezone('America/Vancouver', timezone('UTC', created_at)), 'YYYY-MM-DD HH24:MI:SS')
         ELSE nullif(raw ->> 'receivedDateUF', '') END AS actual_uf,
    ((raw -> 'receivedDate' IS NULL
       AND timezone('America/Vancouver', timezone('UTC', created_at))::date >= filter_day)
      OR (raw -> 'receivedDate' IS NOT NULL AND (raw ->> 'receivedDate')::date >= filter_day))
    AND
    ((raw -> 'receivedDate' IS NULL
       AND timezone('America/Vancouver', timezone('UTC', created_at))::date <= filter_day)
      OR (raw -> 'receivedDate' IS NOT NULL AND (raw ->> 'receivedDate')::date <= filter_day)) AS actual_included
  FROM cases
), checked AS (
  SELECT *, (actual_date IS NOT DISTINCT FROM expected_date)
    AND (actual_uf IS NOT DISTINCT FROM expected_uf)
    AND (actual_included IS NOT DISTINCT FROM expected_included) AS passed
  FROM actual
)
SELECT count(*) AS total, count(*) FILTER (WHERE passed) AS passed,
       bool_and(passed) AS all_passed,
       coalesce(string_agg(label, ', ' ORDER BY label) FILTER (WHERE NOT passed), '(none)') AS failure_labels
FROM checked
\gset raw_receipt_

\echo RAW_RECEIPT_CHECKS passed=:raw_receipt_passed total=:raw_receipt_total failures=:raw_receipt_failure_labels
ROLLBACK;
-- A false result deliberately raises division-by-zero after rollback so psql 12
-- with ON_ERROR_STOP returns a nonzero exit code instead of a false green gate.
SELECT 1 / (:'raw_receipt_all_passed'::boolean::integer) AS raw_receipt_pass;
