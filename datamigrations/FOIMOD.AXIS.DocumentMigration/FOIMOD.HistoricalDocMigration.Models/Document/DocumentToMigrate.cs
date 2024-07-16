using FOIMOD.HistoricalDocMigration.Models.AXISSource;

namespace FOIMOD.HistoricalDocMigration.Models.Document
{
    public  class DocumentToMigrate : AXISDocument
    {
        public int PageSequenceNumber { get; set; }

        public string? PageFilePath { get; set; }

        public Stream FileStream { get; set; }

        public bool HasStreamForDocument { get; set; }

        public string? EmailAttachmentDelimitedString { get; set; }

        public string FolderName { get; set; }

        public string FileType { get; set; }

        public string ParentFolderName { get; set; }

        public string ReviewFlag { get; set; }

        public DateTime ClosingDate { get; set; }

    }
}
