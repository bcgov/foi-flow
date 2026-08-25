using Amazon.S3;
using FOIMOD.CFD.DocMigration.DAL;
using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
using FOIMOD.CFD.DocMigration.Models.FOIFLOWDestination;
using FOIMOD.CFD.DocMigration.Utils;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Logging;

namespace FOIMOD.CFD.DocMigration.BAL;

public class TargetedRecordsMigration
{
    private readonly SqlConnection sourceAxisConnection;
    private readonly IAmazonS3 amazonS3;
    private readonly ILogger logger;
    private readonly TargetedRecordMigrationSettings settings;

    public TargetedRecordsMigration(
        SqlConnection sourceAxisConnection,
        IAmazonS3 amazonS3,
        ILogger logger,
        TargetedRecordMigrationSettings settings)
    {
        this.sourceAxisConnection = sourceAxisConnection;
        this.amazonS3 = amazonS3;
        this.logger = logger;
        this.settings = settings;
    }

    public async Task RunMigration()
    {
        if (settings.Items.Count == 0)
        {
            logger.LogWarning(
                "Targeted records migration is enabled but no items are configured.");
            return;
        }

        var documentsDAL = new DocumentsDAL(sourceAxisConnection);
        var s3Client = new DocMigrationS3Client(amazonS3);
        var recordsRoot = Path.Combine(
            SystemSettings.FileServerRoot,
            SystemSettings.RecordsbaseFolder);

        foreach (var item in settings.Items)
        {
            try
            {
                ValidateItem(item);
                var uploadTarget = TargetedRecordMigrationRules.ResolveUploadTarget(
                    settings.S3BasePath,
                    item);
                var records = documentsDAL.GetRecordsByRequestAndFileName(
                    item.FileNumber,
                    item.FileName);
                var documentID =
                    TargetedRecordMigrationRules.RequireSingleDocumentID(
                        records,
                        item.FileNumber,
                        item.FileName);
                var pages = records!
                    .Where(record => record.IDocID == documentID)
                    .OrderBy(record => record.PageSequenceNumber)
                    .ToList();

                TargetedRecordMigrationRules.ValidateSourceFiles(recordsRoot, pages);

                var containsImages = pages.Any(page =>
                    page.FileType.EndsWith("png", StringComparison.OrdinalIgnoreCase) ||
                    page.FileType.EndsWith("jpeg", StringComparison.OrdinalIgnoreCase) ||
                    page.FileType.EndsWith("jpg", StringComparison.OrdinalIgnoreCase));

                using var pdfStitcher = new DocMigrationPDFStitcher();
                using var documentStream = containsImages
                    ? pdfStitcher.MergeImages(pages, recordsRoot)
                    : pdfStitcher.MergePDFs(pages, recordsRoot);

                var response = await s3Client.UploadFileAsync(new UploadFile
                {
                    AXISRequestID = item.FileNumber.Trim().ToUpperInvariant(),
                    SourceFileName = item.FileName.Trim(),
                    SubFolderPath = uploadTarget.SubFolderPath,
                    DestinationFileName = uploadTarget.DestinationFileName,
                    FileStream = documentStream,
                    UploadType = UploadType.Records
                });

                if (!response.IsSuccessStatusCode)
                {
                    throw new InvalidOperationException(
                        $"S3 returned HTTP {(int)response.StatusCode} ({response.StatusCode}).");
                }

                logger.LogInformation(
                    "Uploaded targeted AXIS record {RequestNumber} / {FileName} to {S3Key}; detector={Detector}",
                    item.FileNumber,
                    item.FileName,
                    $"{uploadTarget.SubFolderPath}/{uploadTarget.DestinationFileName}",
                    item.Detector);
            }
            catch (Exception exception)
            {
                logger.LogError(
                    exception,
                    "Targeted AXIS record upload failed for {RequestNumber} / {FileName}; detector={Detector}",
                    item.FileNumber,
                    item.FileName,
                    item.Detector);
            }
        }
    }

    private static void ValidateItem(TargetedRecordMigrationItem item)
    {
        if (string.IsNullOrWhiteSpace(item.FileNumber) ||
            string.IsNullOrWhiteSpace(item.FileName))
        {
            throw new InvalidOperationException(
                "Each targeted record requires FileNumber and FileName.");
        }
    }
}
