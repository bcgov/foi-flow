# FOI Flow Document Migration Console Application (DocMigration)

This project contains a .NET console application designed to migrate documents, records, and correspondence from the legacy AXIS FOI database to the new FOI Flow system. It handles data extraction, PDF stitching, optical character recognition (OCR), S3 bucket uploading, and extensive database metadata updates.

## Solution Structure

The robust migration process is constructed with the following key components:

- **`FOIMOD.CFD.ConsoleApp.DocMigration`**: The main execution point and console application runner. It handles initialization and reads `appsettings.json`.
- **`FOIMOD.CFD.DocMigration.BAL`**: The Business Access Layer. Contains the core logic for the two primary migration pipelines: `CorrespondenceLogMigration` and `RecordsLogMigration`.
- **`FOIMOD.CFD.DocMigration.DAL`**: The Data Access Layer for reading from the legacy AXIS SQL Server database.
- **`FOIMOD.CFD.DocMigration.FOIFLOW.DAL`**: The Data Access Layer for writing to the modern FOI Flow PostgreSQL databases.
- **`FOIMOD.CFD.DocMigration.Models`**: Contains strongly typed objects representing database rows, S3 payloads, and migration state.
- **`FOIMOD.CFD.DocMigration.OCR`**: Handles optical character recognition processes to convert flat images into searchable PDFs via Tesseract.
- **`FOIMOD.CFD.DocMigration.S3Uploader`**: Wraps the AWS SDK for `.NET` to facilitate pushing stitched PDFs and distinct attachments securely into designated S3 buckets.
- **`FOIMOD.CFD.DocMigration.Utils`**: Contains helper methods, such as the `AXISFolderToMODSectionUtil` which parses the `axistomodsectionmapping.json` for category mapping.

## Prerequisites

To run or develop this application locally, you will need:

1. **.NET SDK**: The target .NET SDK version for this application.
2. **Database Access**: 
   - Read access to the legacy AXIS SQL Server database.
   - Write access to the local/remote FOI Flow PostgreSQL database.
   - Write access to the local/remote FOI Document Reviewer PostgreSQL database.
3. **AWS S3 Credentials**: An Access Key and Secret properly permissioned to write to the requested buckets.
4. **Syncfusion License**: Required for the `DocMigrationPDFStitcher` module to function (PDF manipulation).
5. **Local File Shares**: The host system must have network or direct visibility into the `FileServerRoot` where legacy physical files currently reside.

## Configuration

Settings are driven by `appsettings.json` within the main console app directory, as well as environment variables.

### Key Sections:

**`S3Configuration`**:
- `FileServerRoot`, `CorrespondenceLogBaseFolder`, `RecordsbaseFolder`: The UNC or absolute path to the physical raw document files.
- `AWS_accesskey`, `AWS_secret`, `AWS_S3_Url`: Your S3 target environment configurations.
- `CorrespondenceLogMigration` (boolean): Whether to execute the Correspondence Log pipeline.
- `RecordsMigration` (boolean): Whether to execute the Records Log pipeline.
- `SyncfusionLicense`: The valid application license key.

**`AXISConfiguration`**:
- `SQLConnectionString`: The connection string to the legacy AXIS database.
- `RequestToMigrate`: A comma-separated list of request numbers (e.g. `'CFD-2023-12345', 'CFD-2023-67890'`) denoting which specific FOI requests should be bulk-migrated during this execution run.

**`FOIFLOWConfiguration`**:
- `FOIFLOWConnectionString`: The connection string to the main FOI Flow DB.
- `FOIDocumentReviewerString`: The connection string to the FOI Flow Document Reviewer DB.

## How to Run

1. Open the solution file `FOIMOD.CFD.ConsoleApp.DocMigration.sln` in Visual Studio or your preferred IDE.
2. Navigate to the `FOIMOD.CFD.ConsoleApp.DocMigration` project folder.
3. Configure `appsettings.json` with the appropriate database connection strings, S3 credentials, file paths, and target `RequestToMigrate`.
4. Run the project (F5 in Visual Studio or `dotnet run` from the command line).

Logs will be output directly to the console window and concurrently appended to a daily file formatted as `console_log_{date}.txt` in the executing directory.

## Further Documentation
For detailed insights into the specific migration logic, database mappings, and how AXIS folders translate to FOI Flow Sections, please refer to the `DocMigration_Architecture_and_Mapping.md` file.
