using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FOIMOD.CFD.DocMigration.Models
{
    public static class SystemSettings
    {
        public static string S3_AccessKey { get; set; }

       public static string S3_SecretKey { get; set; }

        public static string S3_EndPoint { get; set; }

        public static string AXISConnectionString{ get; set; }

        public static string FOIFLOWConnectionString { get; set; }

        public static string FOIDocReviewerConnectionString { get; set; }

        public static string RequestToMigrate { get; set; }

        public static string FileServerRoot { get; set; }

        public static string CorrespondenceLogBaseFolder { get; set; }

        public static string RecordsbaseFolder { get; set; }

        public static string S3_Attachements_BasePath { get; set; }

        public static string AttachmentTag { get; set; }

        public static string S3_Attachements_Bucket { get; set; }

        public static string SyncfusionLicense { get; set; }

        public static bool CorrespondenceLogMigration {  get; set; }

        public static bool RecordsMigration { get; set; }

        public static string MinistryRecordsBucket { get; set; }


    }
}
