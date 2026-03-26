# FOIMOD Delete Mode Design

## Goal

Add a request-based delete mode to the migration CLI that previews affected FOIMOD rows by default and only performs destructive deletes when `--confirm-delete` is explicitly provided.

## Scope

The delete mode is limited to the FOIMOD tables that this migration tool currently creates or directly owns:

- `FOIRequestContactInformation`
- `FOIRequestApplicantMappings`
- `FOIRequestApplicants` referenced by those mappings
- `FOIMinistryRequests`
- `FOIRequests`
- `FOIRawRequests`

The delete flow resolves records from `FOIRequests.migrationreference = request_id` and follows existing relationships outward from that parent request.

## CLI Design

Add two flags to the existing CLI:

- `--delete`: switch from migration mode to delete mode
- `--confirm-delete`: required to execute deletes; without it the tool runs preview-only

Delete mode still uses `--input-csv` and `--output-csv`, and it keeps per-request result rows so the current reporting model remains intact.

## Data Flow

For each request id:

1. Resolve the FOI request row using `migrationreference`.
2. If nothing is found, return a `skipped` result with a not-found reason.
3. Collect the related identifiers needed for deletes and previews:
   - `foirequestid/version`
   - `foirawrequestid`
   - linked applicant ids through `FOIRequestApplicantMappings`
4. Count rows in each delete target table.
5. If `--confirm-delete` is not set, return a preview result containing the counts and do not delete anything.
6. If `--confirm-delete` is set, delete rows in FK-safe order inside one transaction and return a `deleted` result.

## Delete Order

The delete order is:

1. `FOIRequestContactInformation`
2. `FOIRequestApplicantMappings`
3. `FOIRequestApplicants`
4. `FOIMinistryRequests`
5. `FOIRequests`
6. `FOIRawRequests`

This order matches the current migration-owned relationships and avoids deleting parent rows before dependent children.

## Error Handling

- Preview mode never commits destructive changes.
- Confirmed delete mode rolls back the request transaction if any delete fails.
- Missing request ids are reported and processing continues with the next request.
- Delete mode and migration mode share the same exit code rule: any failed request returns overall exit code `1`.

## Documentation

Update `README.md` to describe:

- the new delete flags
- preview-vs-confirmed behavior
- delete scope and order
- expected results and examples
