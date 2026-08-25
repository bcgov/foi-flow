namespace FOIMOD.CFD.DocMigration.Models;

public class TargetedRecordMigrationSettings
{
    public bool Enabled { get; set; }

    public string S3BasePath { get; set; } = string.Empty;

    public List<TargetedRecordMigrationItem> Items { get; set; } = new();
}

public class TargetedRecordMigrationItem
{
    public string FileNumber { get; set; } = string.Empty;

    public string FileName { get; set; } = string.Empty;

    public string Key { get; set; } = string.Empty;

    public string Detector { get; set; } = string.Empty;
}

public class TargetedRecordUploadTarget
{
    public string SubFolderPath { get; set; } = string.Empty;

    public string DestinationFileName { get; set; } = string.Empty;
}
