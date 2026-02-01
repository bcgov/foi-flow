using MCS.FOI.AXISIntegration.Utilities.Interfaces;

namespace MCS.FOI.AXISIntegration.Utilities.Types
{
    public class S3Configuration
    {
        public string AWS_accesskey { get; set; }
        public string AWS_secret { get; set; }
        public string AWS_S3_Url { get; set; }
        public string FileServerRoot { get; set; }
        public string CorrespondenceLogBaseFolder { get; set; }
        public string RecordsbaseFolder { get; set; }
        public  string S3_Attachements_BasePath { get; set; }
        public string S3_Attachements_Bucket { get; set; }
        public string AttachmentTag { get; set; }
        public string SyncfusionLicense { get; set; }
        public  string CorrespondenceLogMigration { get; set; }
        public  string RecordsMigration { get; set; }
    }
}
