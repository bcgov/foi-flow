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
- splitting Excel workbooks of request IDs into one workbook per prefix
- generating missing results CSVs in batches from a directory of request CSVs
- consolidating migrated rows from multiple results CSVs into one file
- `dry-run` validation with transaction rollback
- preview-first delete mode with explicit confirmation for destructive deletes
- optional results CSV output
- non-zero exit codes when any request fails

## Repository Structure

- `src/main.py`: CLI entrypoint
- `src/request_splitter.py`: Excel request splitter CLI for generating one workbook per prefix
- `src/batch_generate_results.py`: directory runner for generating missing results CSVs
- `src/consolidate_migrated_results.py`: consolidates migrated rows from results CSVs into one file
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
- ODBC-capable Python database access, typically `pyodbc`
- SQL Server and PostgreSQL ODBC drivers installed on the machine

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

If your environment requires a different Python database package, install the driver your runtime expects and set `AXIS_DB_DRIVER` or `FOIDB_DB_DRIVER` accordingly.

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
- `FOIDB_DB_DRIVER`: Python module used to connect to FOIDB. Default: `pyodbc`
- `DATA_MIGRATION_CREATED_BY`: audit value written into created/updated fields. Default: `cfdmigration`

Example local environment:

```bash
export AXIS_DB_DRIVER=pyodbc
export AXIS_DB_CONNECTION_STRING='DRIVER={ODBC Driver 17 for SQL Server};SERVER=Sphinx\CIRMO,1435;DATABASE=ATIPIPROD;Trusted_Connection=yes;Encrypt=no;'
export AXIS_OFFICE_CODE=CFD
export AXIS_EXCLUDED_STATUSES='Closed,Completed'

export FOIDB_DB_DRIVER=pyodbc
export FOIDB_DB_CONNECTION_STRING='FOIDB_DSN'

export DATA_MIGRATION_CREATED_BY=cfdmigration
```

Notes:

- `AXIS_DB_DRIVER` and `FOIDB_DB_DRIVER` are imported as Python modules. The value must match an installed importable package.
- The connection string format depends on the selected driver.
- The AXIS example above uses Windows integrated authentication through the SQL Server ODBC driver. On Windows, make sure `ODBC Driver 17 for SQL Server` is installed and that your current Windows account is allowed to connect.
- `FOIDB_DB_CONNECTION_STRING` also accepts a bare DSN name such as `FOIDB_DSN`. The application normalizes that to `DSN=FOIDB_DSN;` before connecting.
- `AXIS_EXCLUDED_STATUSES` is trimmed and split on commas. Set it to an empty string to include all statuses.
- Missing required variables cause startup to fail with a `ValueError`.

## Input CSV Format

The input file must contain a `request_id` column. For compatibility with request-splitter output, `Request` is also accepted as a fallback header.

Example:

```csv
request_id
XGR-2020-10982
XGR-2021-00001
```

Behavior:

- blank rows are ignored
- duplicate request IDs are removed while preserving first-seen order
- request IDs with the wrong format are written to the results file as `skipped` with reason `wrong request format`
- a missing `request_id` or `Request` column raises an error before migration starts

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

Generate missing results files for a directory of request CSVs:

```bash
python src/batch_generate_results.py ./output
```

Windows PowerShell:

```powershell
python .\src\batch_generate_results.py .\output
```

Behavior:

- scans the target directory for `*_requests.csv`
- skips any file whose sibling `*_results.csv` already exists
- processes only the first 3 missing results files by default
- accepts `--limit N` to change how many missing files are generated in one run

Consolidate migrated rows from all results files in a directory:

```bash
python src/consolidate_migrated_results.py ./output --output-csv ./output/consolidated_migrated.csv
```

Windows PowerShell:

```powershell
python .\src\consolidate_migrated_results.py .\output --output-csv .\output\consolidated_migrated.csv
```

Behavior:

- scans the target directory for `*_results.csv`
- keeps only rows whose `status` is exactly `migrated`
- writes one consolidated CSV with the standard results columns

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

Skip suffixed request IDs such as `COR-2024-09887-DR` and write them to the results file as skipped:

```bash
python src/main.py \
  --input-csv ./requests.csv \
  --output-csv ./results.csv \
  --skip-suffix-requests
```

Preview what would be deleted for matching FOIMOD records:

```bash
python src/main.py \
  --input-csv ./requests.csv \
  --output-csv ./results.csv \
  --delete
```

Delete matching FOIMOD records after previewing and explicitly confirming:

```bash
python src/main.py \
  --input-csv ./requests.csv \
  --output-csv ./results.csv \
  --delete \
  --confirm-delete
```

Enable debug logging:

```bash
python src/main.py \
  --input-csv ./requests.csv \
  --log-level DEBUG
```

## Excel Request Splitter

Use the Excel splitter when you have a workbook with a `Request` column in column `A` and need one output CSV per request prefix such as `AGR_requests.csv`, `COR_requests.csv`, or `CAF_requests.csv`.

Behavior:

- reads the active sheet and requires `Request` in cell `A1`
- normalizes spacing around hyphens, so values like `COR-2025-40987 - DR` become `COR-2025-40987-DR`
- groups requests by the prefix before the first hyphen
- sorts suffix variants such as `-DR` and `-R` before the base request
- writes one output CSV per prefix with a single `Request` column
- logs and skips invalid request identifiers instead of failing the whole run

Example:

```bash
python src/request_splitter.py \
  --input-xlsx ./MigrationAXIS-724.xlsx \
  --output-dir ./output
```

This creates files like `./output/AGR_requests.csv` and `./output/COR_requests.csv`.

CLI options:

- `--input-csv`: required path to the source CSV
- `--output-csv`: optional path for per-request results
- `--limit`: optional cap on the number of request IDs processed
- `--dry-run`: validate inserts but roll back before commit
- `--delete`: preview or delete FOIMOD rows for each request ID instead of migrating
- `--confirm-delete`: execute deletes when used with `--delete`; otherwise delete mode is preview-only
- `--skip-suffix-requests`: skip request IDs that include a trailing suffix such as `-R` or `-DR`
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
- `preview`: delete mode found rows and reported what would be removed
- `deleted`: delete mode removed rows successfully after confirmation
- `skipped`: request was skipped because it was already migrated, had the wrong format, or matched suffix-skip rules
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

## Delete Flow

For each request ID in `--delete` mode:

1. Find the FOI request in FOIDB by `migrationreference`.
2. If no matching request exists, report the request as `skipped`.
3. Resolve the related records owned by this migration path.
4. Count rows in the delete scope tables and return those counts in preview mode.
5. If `--confirm-delete` is provided, delete rows in FK-safe order inside one transaction.

Delete mode currently targets:

- `FOIRequestContactInformation`
- `FOIRequestApplicantMappings`
- `FOIRequestApplicants`
- `FOIMinistryRequests`
- `FOIRequests`
- `FOIRawRequests`

Without `--confirm-delete`, the tool does not delete anything. It only reports what would be removed.

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
