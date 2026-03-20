# DocMigration Application Architecture & Data Mapping

## Overview
The `FOIMOD.CFD.ConsoleApp.DocMigration` is a structured .NET console application engineered to migrate documents, records, and correspondence from the legacy AXIS database into the modern FOI Flow ecosystem. The application transfers physical files, stitches logical document pages into comprehensive PDFs, pushes them to Amazon S3 buckets, and registers extensive metadata sequentially across multiple PostgreSQL FOI Flow databases.

## Application Flow
The application entry point (`Program.cs`) initializes database connections (AXIS SQL Server, FOIFLOW ODBC, and FOIDocReviewer ODBC) and sets up the S3 client based on `appsettings.json` variables. Depending on the feature flags in the configuration, it delegates processing to two primary pipelines defined in the Business Access Layer (BAL):

1. **Correspondence Log Migration** (`CorrespondenceLogMigration.cs`)
2. **Records Log Migration** (`RecordsLogMigration.cs`)

### 1. Correspondence Log Migration Flow
The correspondence log entails migrating both standalone documents and raw email chains from the legacy AXIS `tblCorrespondence` tables to FOI Flow `FOIMinistryRequestDocuments`.

- **Data Extraction (`DocumentsDAL.cs`)**:
  - The application queries the legacy AXIS SQL Server targeting `tblCorrespondence` joined with `tblRequests`.
  - Scraped fields include: `vcVisibleRequestID` (Request Number), `vcSubject`, `sdtMailedDate`, `vcEmail`, `vcFromEmail`, `vcBody` (the email message body), and an aggregated pipe-delimited string representing all attachments.

- **Processing & File Movement (`CorrespondenceLogMigration.cs`)**:
  - The process evaluates if the row represents an **Email** or a **Standalone Record** by checking for the presence of email body/recipient fields.
  - **Standalone Records (Non-Emails)**: 
    - The code splits the delimited attachment references and creates a universal UNC path utilizing the `FileServerRoot` & `CorrespondenceLogBaseFolder`.
    - It reads the file over the network and directly uploads it to the AWS S3 target bucket under a dynamically generated path: `{S3_Attachements_BasePath}/{AXISRequestNumber}/{AttachmentTag}/{NewGuid}.ext`.
  - **Email Threads**:
    - The system invokes `DocMigrationPDFStitcher.CreatePDFDocument()` to synthetically compose a master PDF file containing the parsed Email Body, Subject, Date, and "To/From" information.
    - It then examines all attached files sequentially. If an attachment is a non-PDF (e.g., `.docx`), it uploads it to S3 independently immediately.
    - If an attachment is a `.pdf`, it gets memory-stitched directly into the rear of the master Email PDF file.
    - The compiled and stitched Email Thread PDF is finally uploaded to S3.

- **FOI Flow Database Insertion (`AttachmentsDAL.cs`)**:
  - For every file successfully pushed to S3, `InsertIntoMinistryRequestDocuments` is called against the FOI Flow PostgreSQL database.
  - An `INSERT INTO public."FOIMinistryRequestDocuments"` is executed.
  - Crucial mappings dynamically created during the insert:
    - `documentpath`: The complete constructed S3 URL containing the file.
    - `category`: Hardcoded to `'applicant'`.
    - `createdby`: Hardcoded to `'cfdmigration'`.
    - `foiministryrequest_id` and `foiministryrequestversion_id`: The system looks up the FOI ministry request ID backwards by matching the incoming target AXIS `requestnumber` against the `FOIMinistryRequests` table.

### 2. Records Log Migration Flow
- **Data Source**: Reconstructs complete records by collecting sequential pages from AXIS (`tblDocuments`, `tblPages`, `tblDocumentReviewLog`, and `tblRedactionLayers`).
- **Processing Logic**:
  - Extracts raw document pages related to a unique `iDocID`.
  - Determines if the collection contains images (`.png`, `.jpg`).
  - Utilizes `HugeMemoryStream` paired with `DocMigrationPDFStitcher` to compile standard PDF (`MergePDFs`) or image-heavy PDFs (`MergeImages`) into cohesive document bundles.
  - Following the successful S3 bucket extraction (`MinistryRecordsBucket`), the application conducts sophisticated multi-table data seeding via `RecordsDAL`.
  - **Affected Destination Tables**:
    - `FOIRequestRecords`
    - `DocumentMaster`
    - `Documents`
    - `DocumentAttributes`
    - `DocumentHashCodes`
    - `DeduplicationJob`
    - `DocumentPageFlags` (captures "NOT RELEVANT" or "DUPLICATE" flags from the AXIS `tblPageReviewFlags`).

### Source Legacy Database Tables (AXIS SQL Server)
The migration relies on extracting relational data from several key legacy AXIS tables:

- **`tblRequests`**: The central table representing an FOI Request. We query this to match the target `vcVisibleRequestID` (e.g., CFD-2023-xxxx).
- **`tblCorrespondence`**: Houses standalone file attachments and email communications belonging to a request, including the email body (`vcBody`), subjects, and recipient details.
- **`tblDocuments` / `tblPages`**: Form the core of the **Records Log Migration**. `tblDocuments` represents logical folders/documents, while `tblPages` holds the individual page files (images/PDFs) mapped to that document.
- **`tblDocumentReviewLog` / `tblRedactionLayers`**: Determine which exact documents/pages are considered the final "Request Records" to be migrated, excluding drafts or intermediate versions.
- **`tblPageReviewFlags`**: Used to identify if a specific page of a record was previously marked as "DUPLICATE" or "NOT RELEVANT".

### Destination FOI Flow Database Tables (PostgreSQL)

The extracted data is seeded across a complex web of modern PostgreSQL tables, split primarily between the core `FOI Flow` database and the `FOI Document Reviewer` database.

#### Core FOI Flow Tables (`FOIFLOWConnectionString`):
- **`FOIMinistryRequests`**: The master table in the new system. The migration queries this table *backwards* using the `axisrequestid` to find the correct `foiministryrequest_id` and `version` to link new records against.
- **`FOIMinistryRequestDocuments`**: The final resting place for correspondence logs and standalone files uploaded to S3.
- **`FOIRequestRecords`**: Stores the primary metadata for **Records Log Migration**, including the calculated `attributes` JSON which holds the migrated system Section ID (`divisionid`), file size, and batch tracking.
- **`ProgramAreaDivisions`**: Queried during mapping to translate string-based section names (e.g., "ADOPTION") into their corresponding numeric database `divisionid`.

#### FOI Document Reviewer Tables (`FOIDocumentReviewerString`):
*(Used exclusively during the Records Log Migration for advanced metadata)*
- **`DocumentMaster`**: Maintains the highest-level link between the S3 file path and the FOI Request.
- **`Documents`**: Tracks individual document metadata like page counts and system status.
- **`DocumentAttributes`**: Mirrors the JSON attributes (file size, section ID) but stored within the Document Reviewer domain.
- **`DocumentHashCodes`**: Generates and stores unique hashes used later for document deduplication workflows.
- **`DeduplicationJob`**: Records a successful migration event as a completed deduplication job type (`recordupload`).
- **`DocumentPageFlags`**: Migrates the legacy AXIS page flags ("DUPLICATE", "NOT RELEVANT") into the new system format so the target application knows which specific pages inside the PDF should be visually flagged.

---

## AXIS to FOIMOD Domain Mapping

During the **Records Log Migration**, legacy categorization terminology (Axis Folders) must be consistently translated into modern application categorization structures (MOD Sections). 

### The Mapping Logic Pipeline

1. **JSON Configuration Dictator**: The translation matrix is explicitly defined in a local JSON configuration document: `axistomodsectionmapping.json` (inside the `sectionmapping` solution folder).
2. **Key Lookups (`AXISFolderToMODSectionUtil`)**: For any clustered PDF upload, the application pulls the original `FolderName` allocated in AXIS. It invokes the utility which parses the JSON schema and returns the translated target FOIMOD Section Name string.
3. **Database ID Translation (`RecordsDAL.GetSectionIDByName`)**: The string name relies on database truth. The `RecordsDAL` queries the FOIFLOW `ProgramAreaDivisions` table specifically targeting sections connected to the 'MCF' program area to accurately resolve the valid target `divisionid`.
4. **Metadata Construction**: The resolved `divisionid` is injected into a specific string-formatted JSON structure (`attributes` field) alongside file sizes and dynamic batch numbers. This JSON is subsequently written into `FOIRequestRecords` to solidify the translated linkage in the new application lifecycle.

### Common Mapping Examples
A sample of standardized translations dictated by the JSON mapping engine:
- `"Adoption"` maps logically to `"ADOPTION"`
- `"CLINICAL HISTORY"` standardizes to `"MEDICAL"`
- `"EducationTrainingPlanning"` streamlines to `"EDUCATION, EMPLOYMENT AND TRAINING"`
- `"HISTORY & RECORDING (PHOTOS)"` maps into `"PERSONAL HISTORY AND RECORDING"`
- `"Out Of Care"` transitions to `"OUT OF CARE SERVICES"`
- `"YoungOffender"` cleanly transitions to `"YOUNG OFFENDERS ACT"`
