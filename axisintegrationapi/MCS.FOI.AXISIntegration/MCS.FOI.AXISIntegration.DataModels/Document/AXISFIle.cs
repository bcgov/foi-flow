using System;
using System.IO;

namespace MCS.FOI.AXISIntegration.DataModels.Document
{
    public class AXISFile
    {
        public string AXISRequestID { get; set; }
        public int? CorrespondenceID { get; set; }
        public string? FilePathOnServer { get; set; }
        public string? FileName { get; set; }
        public string? FileExtension => !string.IsNullOrEmpty(FileName) 
            ? Path.GetExtension(FileName).TrimStart('.') 
            : null;
        public string? EmailContent { get; set; }
        public string? EmailDate { get; set; }
        public string? EmailTo { get; set; }
        public string? EmailFrom { get; set; }
        public string? EmailSubject { get; set; }
        public string? CorrespondenceType { get; set; }
        public string? AttachmentName { get; set; }
    }
}
