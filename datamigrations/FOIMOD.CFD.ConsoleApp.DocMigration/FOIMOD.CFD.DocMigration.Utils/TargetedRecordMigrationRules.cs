using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;

namespace FOIMOD.CFD.DocMigration.Utils;

public static class TargetedRecordMigrationRules
{
    public static TargetedRecordUploadTarget ResolveUploadTarget(
        string s3BasePath,
        TargetedRecordMigrationItem item)
    {
        ArgumentNullException.ThrowIfNull(item);

        var basePath = s3BasePath?.Trim().Trim('/') ?? string.Empty;
        var key = item.Key?.Trim() ?? string.Empty;
        var fileNumber = item.FileNumber?.Trim() ?? string.Empty;

        if (string.IsNullOrWhiteSpace(basePath))
        {
            throw new InvalidOperationException(
                "TargetedRecordsMigration:S3BasePath is required.");
        }

        if (key.Contains('\\') || key.StartsWith('/'))
        {
            throw new InvalidOperationException("The configured S3 key is invalid.");
        }

        var keyParts = key.Split('/', StringSplitOptions.RemoveEmptyEntries);
        if (keyParts.Length != 2 ||
            keyParts.Any(part => part is "." or "..") ||
            !keyParts[0].Equals(fileNumber, StringComparison.OrdinalIgnoreCase) ||
            !keyParts[1].EndsWith(".pdf", StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException(
                $"The configured S3 key must be '<file number>/<file name>.pdf' for {fileNumber}.");
        }

        return new TargetedRecordUploadTarget
        {
            SubFolderPath = $"{basePath}/{keyParts[0]}",
            DestinationFileName = keyParts[1]
        };
    }

    public static int RequireSingleDocumentID(
        IEnumerable<DocumentToMigrate>? records,
        string requestNumber,
        string fileName)
    {
        var documentIDs = records?
            .Select(record => record.IDocID)
            .Distinct()
            .ToArray() ?? Array.Empty<int>();

        if (documentIDs.Length == 0)
        {
            throw new InvalidOperationException(
                $"No AXIS record matched request {requestNumber} and file '{fileName}'.");
        }

        if (documentIDs.Length > 1)
        {
            throw new InvalidOperationException(
                $"More than one AXIS document matched request {requestNumber} and file '{fileName}'.");
        }

        return documentIDs[0];
    }

    public static void ValidateSourceFiles(
        string recordsRoot,
        IEnumerable<DocumentToMigrate> pages)
    {
        var allowedRoot = Path.GetFullPath(recordsRoot);

        foreach (var page in pages)
        {
            var fullPath = Path.GetFullPath(Path.Combine(
                allowedRoot,
                page.SiFolderID,
                page.PageFilePath ?? string.Empty));
            var relativePath = Path.GetRelativePath(allowedRoot, fullPath);

            if (relativePath == ".." ||
                relativePath.StartsWith(
                    $"..{Path.DirectorySeparatorChar}",
                    StringComparison.Ordinal) ||
                Path.IsPathRooted(relativePath))
            {
                throw new InvalidOperationException(
                    "The resolved AXIS page path is outside the configured records root.");
            }

            if (!File.Exists(fullPath))
            {
                throw new FileNotFoundException(
                    "An AXIS page file was not found.",
                    fullPath);
            }
        }
    }
}
