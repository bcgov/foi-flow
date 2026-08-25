# Targeted Records Migration Runbook

This runbook explains how to configure and run the targeted AXIS records migration. This workflow rebuilds selected records from AXIS and uploads them to S3 without updating the FOI Flow or document-reviewer databases.

## What the workflow does

For every configured item, the application:

1. finds the AXIS request using `FileNumber`;
2. finds the AXIS document using its generated logical `FileName`;
3. retrieves every physical page belonging to the matched AXIS document;
4. reads those pages from the AXIS file share;
5. stitches or converts them into one PDF;
6. uploads the PDF to the configured S3 path while preserving the filename from `Key`; and
7. logs the result without writing database metadata.

The workflow trusts AXIS for the page list. It does not use or validate an external expected page count.

## Prerequisites

The machine running the console application needs:

- the .NET SDK required by the solution;
- network access to the AXIS SQL Server database;
- read access to the AXIS document file share;
- network access to the configured S3-compatible endpoint;
- S3 credentials permitted to write to the target path; and
- a valid Syncfusion license when the selected files require Syncfusion processing.

The application currently targets .NET 7. The build emits an end-of-support warning for that framework, so plan an upgrade separately from the migration run.

## Configure appsettings.json

Edit:

```text
FOIMOD.CFD.ConsoleApp.DocMigration/appsettings.json
```

### 1. Configure the AXIS file share

```json
"S3Configuration": {
  "FileServerRoot": "\\\\solis\\ATIPDocs\\",
  "RecordsbaseFolder": "AFXWDOCS"
}
```

The application resolves physical AXIS pages as:

```text
<FileServerRoot>\<RecordsbaseFolder>\<siFolderID>\<AXIS page filename>
```

For the example above:

```text
\\solis\ATIPDocs\AFXWDOCS\<siFolderID>\<AXIS page filename>
```

Confirm that the account running the application can read this UNC location.

### 2. Configure the S3 endpoint and credentials

```json
"S3Configuration": {
  "AWS_accesskey": "",
  "AWS_secret": "",
  "AWS_S3_Url": "https://citz-foi-prod.objectstore.gov.bc.ca"
}
```

Prefer providing credentials through environment variables rather than saving secrets in `appsettings.json`:

```text
S3Configuration__AWS_accesskey
S3Configuration__AWS_secret
```

The application loads environment variables after the JSON file, so environment-variable values override matching JSON settings.

Do not commit real credentials.

### 3. Configure the AXIS database connection

```json
"AXISConfiguration": {
  "SQLConnectionString": "Data Source=.;Initial Catalog=ATIPD;Integrated Security=True;Encrypt=False"
}
```

This connection is read-only for the targeted workflow. It is used to locate the AXIS request, document, and page rows.

The connection string can also be provided using:

```text
AXISConfiguration__SQLConnectionString
```

### 4. Disable database-writing migration flows

Set both existing flows to `False`:

```json
"S3Configuration": {
  "CorrespondenceLogMigration": "False",
  "RecordsMigration": "False"
}
```

This is important. The original `RecordsMigration` workflow writes metadata to the FOI Flow and document-reviewer databases. It must remain disabled for an upload-only repair run.

### 5. Configure the targeted records

```json
"TargetedRecordsMigration": {
  "Enabled": true,
  "S3BasePath": "syncfusion_fix",
  "Items": [
    {
      "FileNumber": "CFD-2022-23413",
      "FileName": "FS CPF 1-56896804953 VOL 3 - 23413_INTAKE AND INCIDENT SERVICE REQUEST AND MEMO.pdf",
      "Key": "CFD-2022-23413/016d1094-eda4-456d-b139-e3c2ae1d4f31.pdf",
      "Detector": "syncfusion"
    },
    {
      "FileNumber": "CFD-2022-23413",
      "FileName": "FS CPF 1-56896804953 VOL 4 - 23413_MEDICAL.pdf",
      "Key": "CFD-2022-23413/13d89576-801d-4e36-ba63-fb03781e5510.pdf",
      "Detector": "syncfusion"
    }
  ]
}
```

Configuration fields:

| Field | Required | Description |
|---|---|---|
| `Enabled` | Yes | Set to `true` to run the targeted workflow. |
| `S3BasePath` | Yes | S3 bucket or top-level namespace, such as `syncfusion_fix`. |
| `FileNumber` | Yes | AXIS visible request number, such as `CFD-2022-23413`. |
| `FileName` | Yes | Logical PDF name used to identify the AXIS document. |
| `Key` | Yes | Request directory and existing UUID filename to preserve. |
| `Detector` | No | Audit value included in logs. It does not select the merger. |

## Key requirements

Each `Key` must have exactly this form:

```text
<FileNumber>/<existing filename>.pdf
```

For example:

```text
CFD-2022-23413/016d1094-eda4-456d-b139-e3c2ae1d4f31.pdf
```

The request directory in `Key` must match `FileNumber`. The workflow rejects backslashes, traversal segments, non-PDF filenames, and keys assigned to a different request.

The final S3 key combines `S3BasePath` and `Key`:

```text
syncfusion_fix/CFD-2022-23413/016d1094-eda4-456d-b139-e3c2ae1d4f31.pdf
```

The UUID filename is preserved; the targeted workflow does not generate a new UUID.

## FileName requirements

`FileName` is the logical records filename produced by the original records migration:

```text
<AXIS parent document name>_<AXIS document name>.pdf
```

The migration removes apostrophes from both AXIS document-name components before comparing the result with `FileName`.

If no document matches, the item is logged as failed. If more than one AXIS `iDocID` has the same logical filename within the request, the item is considered ambiguous and is not uploaded.

## Build the application

From the repository directory containing the solution:

```bash
dotnet restore FOIMOD.CFD.ConsoleApp.DocMigration.sln
dotnet build FOIMOD.CFD.ConsoleApp.DocMigration.sln
```

The solution currently reports known framework and dependency warnings. Review them, but distinguish existing warnings from build errors. Do not run the migration if the build reports an error.

## Run the application

Run from the console-application project directory so `appsettings.json` is found consistently:

```bash
cd FOIMOD.CFD.ConsoleApp.DocMigration
dotnet run
```

Alternatively, from the solution directory:

```bash
dotnet run --project FOIMOD.CFD.ConsoleApp.DocMigration/FOIMOD.CFD.ConsoleApp.DocMigration.csproj
```

The process reads the targeted configuration at startup and processes the items sequentially.

## Expected output

The console should include messages similar to:

```text
TargetedRecordsMigration Starting...
Uploaded targeted AXIS record CFD-2022-23413 / <logical filename> to syncfusion_fix/CFD-2022-23413/<UUID>.pdf; detector=syncfusion
TargetedRecordsMigration Completed
```

The application also writes a local console log file. Review both the console and log file for failures.

One failed item does not stop the next configured item. Therefore, a final `Completed` message means the item loop ended; verify that every item has its own successful upload log entry.

## Verify the uploaded files

After the run:

1. Confirm that every configured key exists under `S3BasePath`.
2. Confirm that each uploaded object retained its configured UUID filename.
3. Download or inspect each PDF using an approved method.
4. Confirm that the PDF opens and contains the AXIS pages in the expected order.
5. Compare the successful upload logs with the configured item list.

The targeted workflow intentionally does not update database metadata, so database changes are not expected.

## Disable the workflow after the run

If the configuration will be reused, set:

```json
"TargetedRecordsMigration": {
  "Enabled": false
}
```

This prevents the same files from being uploaded again during a later console-app run.

## Troubleshooting

### No AXIS record matched

Check:

- `FileNumber` exactly matches `tblRequests.vcVisibleRequestID`;
- `FileName` matches `<parent document>_<document>.pdf`;
- apostrophes have been removed from the logical name; and
- the document appears in the request review log, its section list, or a non-delivery redaction layer.

### More than one AXIS document matched

The logical filename is ambiguous within the request. Identify the intended AXIS `iDocID` before changing or rerunning the migration. The workflow does not guess between matches.

### AXIS page file was not found

Check:

- `FileServerRoot` and `RecordsbaseFolder`;
- access to the UNC share;
- the process account's file-share permissions;
- the AXIS `siFolderID`; and
- the physical `tblPages.vcFileName` value.

### Configured S3 key is invalid

Ensure the key:

- contains only one request directory and one PDF filename;
- uses `/`, not `\`;
- starts with the same value as `FileNumber`; and
- ends with `.pdf`.

### S3 upload returned an error

Check:

- the S3 endpoint;
- access key and secret;
- write permission for `S3BasePath`;
- whether `syncfusion_fix` is the correct bucket/top-level namespace; and
- the HTTP status code in the error log.

### Application appears to finish successfully after an item error

This is expected loop behavior. Errors are isolated per item so later records can still run. Treat the migration as successful only after every configured item has an explicit successful upload log entry.

## Related documentation

- `AXIS_FILE_LOCATION_QUERY.md` explains the AXIS lookup, physical-page resolution, stitching, and no-database-update behavior.
- `README.md` provides the general solution build and configuration overview.
