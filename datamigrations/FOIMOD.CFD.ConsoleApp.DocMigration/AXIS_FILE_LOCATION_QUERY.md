# Targeted AXIS Records Migration to S3

This project includes an upload-only workflow for rebuilding selected records from AXIS and sending them to S3. It is separate from the original bulk `RecordsMigration` workflow and does not update the FOI Flow or document-reviewer databases.

## Configuration

Keep the original database-writing records flow disabled:

```json
"S3Configuration": {
  "CorrespondenceLogMigration": "False",
  "RecordsMigration": "False"
}
```

Configure the records that need to be rebuilt under `TargetedRecordsMigration`:

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

The fields mean:

| Field | Purpose |
|---|---|
| `Enabled` | Enables only the targeted upload workflow. |
| `S3BasePath` | Bucket or top-level S3 path used by the existing pre-signed URL implementation. |
| `FileNumber` | AXIS visible request number from `tblRequests.vcVisibleRequestID`. |
| `FileName` | Logical PDF name generated from `<parent document>_<document>.pdf`. |
| `Key` | Request directory and existing UUID filename that must be preserved. |
| `Detector` | Audit value written to logs; it does not choose the PDF engine. |

There is no expected-page-count setting. AXIS is the source of truth, and the workflow stitches every page AXIS returns for the matched document.

## Output keys

The workflow combines `S3BasePath` with each configured `Key`. The examples produce:

```text
syncfusion_fix/CFD-2022-23413/016d1094-eda4-456d-b139-e3c2ae1d4f31.pdf
syncfusion_fix/CFD-2022-23413/13d89576-801d-4e36-ba63-fb03781e5510.pdf
```

The UUID filename is not regenerated. `TargetedRecordMigrationRules.ResolveUploadTarget` validates that:

- the key has the form `<FileNumber>/<filename>.pdf`;
- the request directory equals `FileNumber`;
- the key does not contain traversal or backslash segments; and
- the S3 base path is present.

## How the AXIS record is found

`DocumentsDAL.GetRecordsByRequestAndFileName` uses a parameterized query created by `RecordLookupQuery`. The lookup:

1. resolves `FileNumber` to `tblRequests.iRequestID`;
2. reproduces the original records selection from `tblDocumentReviewLog`, its section lists, and `tblRedactionLayers`;
3. builds the logical filename from the AXIS parent and document names;
4. removes apostrophes in the same way as the original `RecordsLogMigration`; and
5. returns every `tblPages` row for the matched `iDocID`, ordered by `siPageNum`.

The query uses `@RequestNumber` and `@FileName` parameters. It does not insert values with `string.Format`.

The logical filename comparison is equivalent to:

```sql
CONCAT(
    REPLACE(ParentD.vcDocName, '''', ''),
    '_',
    REPLACE(D.vcDocName, '''', ''),
    '.pdf'
) = @FileName
```

The workflow rejects the item when AXIS returns:

- no `iDocID`, because the configured request/file pair was not found; or
- more than one distinct `iDocID`, because the logical filename is ambiguous.

A failure for one configured item is logged and does not stop the remaining items.

## Physical AXIS files

Each returned page is read from:

```text
<FileServerRoot>\<RecordsbaseFolder>\<siFolderID>\<tblPages.vcFileName>
```

Using the sample configuration, that is approximately:

```text
\\solis\ATIPDocs\AFXWDOCS\<siFolderID>\<page filename>
```

Before stitching, `TargetedRecordMigrationRules.ValidateSourceFiles` verifies that every resolved page remains under the configured records root and exists on disk. The application host must have access to the AXIS UNC share.

## Stitching and conversion

All AXIS page rows for the selected `iDocID` are ordered by `siPageNum`.

- If any returned page has a PNG, JPEG, or JPG extension, the workflow calls `DocMigrationPDFStitcher.MergeImages`.
- Otherwise, it calls `DocMigrationPDFStitcher.MergePDFs`.

The resulting PDF stream is uploaded directly. The workflow does not compare its page count with an external value; it trusts the pages selected from AXIS.

## S3 upload

The workflow passes these values to `DocMigrationS3Client.UploadFileAsync`:

```text
SubFolderPath      = syncfusion_fix/CFD-2022-23413
DestinationFileName = 016d1094-eda4-456d-b139-e3c2ae1d4f31.pdf
```

The existing S3 helper creates the pre-signed PUT URL from:

```csharp
$"{file.SubFolderPath}/{file.DestinationFileName}"
```

Although `UploadFile.S3BucketName` exists, the current helper does not use it. `S3BasePath` must therefore contain the correct bucket or top-level namespace for the configured S3 endpoint.

An upload is successful only when `HttpResponseMessage.IsSuccessStatusCode` is true.

## No database updates

`TargetedRecordsMigration` depends only on:

- the AXIS SQL Server connection for reading document/page information;
- the AXIS file share for reading physical pages; and
- the S3 client for uploading the rebuilt PDF.

It does not create `RecordsDAL` and does not call any of these original metadata operations:

- `InsertIntoFOIRequestRecords`;
- `InsertIntoDocumentMaster`;
- `InsertIntoDocuments`;
- `InsertIntoDocumentAttributes`;
- `InsertIntoDocumentHashcodes`;
- `InsertIntoDeduplicationJob`; or
- `InsertDocumentPageFlags`.

Leave `S3Configuration:RecordsMigration` set to `False` when running this targeted repair so the original database-writing workflow does not run afterward.

## Running the migration

1. Set the AXIS connection string and S3 credentials using the existing configuration/environment-variable mechanism.
2. Confirm `FileServerRoot` and `RecordsbaseFolder` point to the accessible AXIS file share.
3. Keep `RecordsMigration` and `CorrespondenceLogMigration` disabled.
4. Set `TargetedRecordsMigration:Enabled` to `true`.
5. Add or remove items from `TargetedRecordsMigration:Items`.
6. Verify each `Key` contains the required original UUID filename.
7. Run the console application.
8. Review logs for one success or failure entry per configured item.
9. Set `TargetedRecordsMigration:Enabled` back to `false` after the repair run if the same configuration will be reused.

## Implementation references

- `FOIMOD.CFD.ConsoleApp.DocMigration/Program.cs` reads the targeted configuration and starts the workflow.
- `FOIMOD.CFD.DocMigration.Models/TargetedRecordMigrationSettings.cs` defines the configuration and upload-target models.
- `FOIMOD.CFD.DocMigration.DAL/RecordLookupQuery.cs` contains the parameterized AXIS query.
- `FOIMOD.CFD.DocMigration.DAL/DocumentsDAL.cs` maps the AXIS rows into `DocumentToMigrate` pages.
- `FOIMOD.CFD.DocMigration.BAL/TargetedRecordsMigration.cs` coordinates lookup, validation, stitching, and upload without database writes.
- `FOIMOD.CFD.DocMigration.Utils/TargetedRecordMigrationRules.cs` validates AXIS matches, source paths, and S3 keys.
- `FOIMOD.CFD.DocMigration.Utils/DocMigrationPDFStitcher.cs` builds the final PDF stream.
- `FOIMOD.CFD.DocMigration.Utils/DocMigrationS3Client.cs` uploads the PDF stream.
