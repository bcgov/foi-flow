# data_migration

Python utility for migrating FOI request records from AXIS into FOIDB using a CSV of request IDs.

## Overview

This project reads AXIS request identifiers from an input CSV, loads the corresponding request data from the AXIS database, maps that data into FOIDB payloads, and inserts the records into FOIDB.

The migration currently handles:

- parent FOI request records
- ministry request records
- applicant records
- applicant mapping records
- contact information records

The tool supports:

- duplicate filtering in the input CSV
- skipping requests already migrated into FOIDB
- `dry-run` validation with transaction rollback
- optional results CSV output
- non-zero exit codes when any request fails

## Repository Structure

- `src/main.py`: CLI entrypoint
- `src/migrator.py`: orchestration and per-request transaction flow
- `src/axis_client.py`: AXIS read queries
- `src/foidb_client.py`: FOIDB lookups and inserts
- `src/mappers/`: AXIS-to-FOIDB payload mapping logic
- `src/csv_reader.py`: input CSV parsing and deduplication
- `src/results_writer.py`: optional results CSV writer
- `tests/`: unit tests for parsing, mapping, migration flow, and result writing

## Prerequisites

Local execution assumes:

- Python 3.11 or newer
- access to the source AXIS database
- access to the target FOIDB PostgreSQL database
- a SQL Server Python driver for AXIS access, typically `pyodbc`
- a PostgreSQL Python driver for FOIDB access, typically `psycopg`
- system-level ODBC support if `pyodbc` is used

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Windows Command Prompt:

```bat
py -3 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
```

Install the Python dependencies used by this project:

```bash
python -m pip install -r requirements.txt
```

If your environment requires a different PostgreSQL package, install the driver your runtime expects and set `FOIDB_DB_DRIVER` accordingly.

Create a local environment file from the sample:

```bash
cp .env_sample .env
```

On Windows, use:

```powershell
Copy-Item .env_sample .env
```

Edit `.env` with the correct database connection values for your environment, then load it before running the migration:

```bash
set -a
source ./.env
set +a
```

Windows PowerShell does not support `source` or `set -a`. Either set the variables manually in your shell, or load them from `.env` before each run:

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
  $name, $value = $_ -split '=', 2
  [System.Environment]::SetEnvironmentVariable($name, $value.Trim("'`""), 'Process')
}
```

Windows Command Prompt users can set variables manually with `set VAR_NAME=value` before running commands.

## Configuration

The migration reads configuration from environment variables.

Required variables:

- `AXIS_DB_CONNECTION_STRING`
- `FOIDB_DB_CONNECTION_STRING`

Optional variables:

- `AXIS_DB_DRIVER`: Python module used to connect to AXIS. Default: `pyodbc`
- `AXIS_OFFICE_CODE`: AXIS office code used to scope source queries and FOIDB program area lookup. Default: `CFD`
- `AXIS_EXCLUDED_STATUSES`: comma-separated AXIS request statuses to exclude. Default: `Closed,Completed`
- `FOIDB_DB_DRIVER`: Python module used to connect to FOIDB. Default: `psycopg`
- `DATA_MIGRATION_CREATED_BY`: audit value written into created/updated fields. Default: `cfdmigration`

Example local environment:

```bash
export AXIS_DB_DRIVER=pyodbc
export AXIS_DB_CONNECTION_STRING='DRIVER={ODBC Driver 18 for SQL Server};SERVER=axis-host;DATABASE=AXIS;UID=axis_user;PWD=axis_password;Encrypt=yes;TrustServerCertificate=yes'
export AXIS_OFFICE_CODE=CFD
export AXIS_EXCLUDED_STATUSES='Closed,Completed'

export FOIDB_DB_DRIVER=psycopg
export FOIDB_DB_CONNECTION_STRING='host=foidb-host dbname=foidb user=foidb_user password=foidb_password port=5432'

export DATA_MIGRATION_CREATED_BY=cfdmigration
```

Notes:

- `AXIS_DB_DRIVER` and `FOIDB_DB_DRIVER` are imported as Python modules. The value must match an installed importable package.
- The connection string format depends on the selected driver.
- `AXIS_EXCLUDED_STATUSES` is trimmed and split on commas. Set it to an empty string to include all statuses.
- Missing required variables cause startup to fail with a `ValueError`.

## Input CSV Format

The input file must contain a `request_id` column.

Example:

```csv
request_id
XGR-2020-10982
XGR-2021-00001
```

Behavior:

- blank rows are ignored
- duplicate request IDs are removed while preserving first-seen order
- a missing `request_id` column raises an error before migration starts

## Running the Migration

Basic run:

```bash
python src/main.py \
  --input-csv ./requests.csv
```

Windows PowerShell:

```powershell
python .\src\main.py --input-csv .\requests.csv
```

Windows Command Prompt:

```bat
python .\src\main.py --input-csv .\requests.csv
```

Write a results file:

```bash
python src/main.py \
  --input-csv ./requests.csv \
  --output-csv ./results.csv
```

Validate only without committing:

```bash
python src/main.py \
  --input-csv ./requests.csv \
  --output-csv ./results.csv \
  --dry-run
```

Process only the first 10 request IDs:

```bash
python src/main.py \
  --input-csv ./requests.csv \
  --limit 10
```

Enable debug logging:

```bash
python src/main.py \
  --input-csv ./requests.csv \
  --log-level DEBUG
```

CLI options:

- `--input-csv`: required path to the source CSV
- `--output-csv`: optional path for per-request results
- `--limit`: optional cap on the number of request IDs processed
- `--dry-run`: validate inserts but roll back before commit
- `--log-level`: Python logging level, default `INFO`

## Output and Exit Codes

If `--output-csv` is provided, the tool writes one row per processed request with these columns:

- `request_id`
- `status`
- `reason`
- `foirequest_id`
- `started_at`
- `finished_at`

Status values produced by the current implementation:

- `migrated`: request committed successfully
- `dry-run`: request validated and rolled back intentionally
- `skipped`: FOIDB already contains the request
- `failed`: the request could not be migrated

Exit code behavior:

- `0` if all processed requests are `migrated`, `dry-run`, or `skipped`
- `1` if any processed request ends with `failed`

## Migration Flow

For each request ID:

1. Check whether FOIDB already contains a matching `migrationreference`.
2. Start the FOIDB transaction boundary.
3. Load the parent AXIS request record.
4. Fail and roll back if the parent request is missing.
5. Map and insert the parent FOI request into `FOIRequests`.
6. Load and insert the ministry request when present.
7. Load, map, and insert applicant records and applicant mappings.
8. Load, map, and insert contact information rows.
9. Commit the transaction, or roll it back on error.

In `--dry-run` mode, the tool performs the same reads, mappings, lookups, and insert attempts, then rolls back instead of committing.

## Architecture Notes

The code is intentionally split into a few small layers:

- `AxisClient` encapsulates SQL Server reads.
- `FoidbClient` encapsulates FOIDB lookups and inserts.
- mapper modules translate raw AXIS rows into FOIDB payloads.
- `RequestMigrator` coordinates the request-level workflow and transaction handling.
- `main.run()` handles CLI parsing, settings loading, CSV input, and result aggregation.

This separation keeps query logic, mapping rules, and orchestration concerns isolated enough to test independently.

## Testing

Run the test suite with:

```bash
python -m pytest
```

Windows PowerShell:

```powershell
python -m pytest
```

Windows Command Prompt:

```bat
python -m pytest
```

Current tests cover:

- input CSV validation and deduplication
- request mapping behavior
- migration success, skip, and failure flows
- optional results CSV writing from the CLI path

## Notes and Limitations

- This project now includes a minimal `requirements.txt` for local setup, but it does not yet separate runtime and development dependencies.
- The current implementation assumes driver modules expose a top-level `connect()` function.
- `FoidbClient.begin_request()` is a no-op in the current code; transaction behavior depends on the FOIDB driver connection defaults.
- AXIS office scoping and excluded statuses are configurable through environment variables rather than hard-coded in SQL.
- The migration uses FOIDB lookup tables for received mode, applicant category, program area, request status, and requestor type. Missing required lookup values will fail the request.
- Existing migrated requests are identified by `migrationreference`.
