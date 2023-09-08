using FOIMOD.CFD.DocMigration.Models.AXISSource;

namespace FOIMOD.CFD.DocMigration.Models.Document
{
    public  class DocumentToMigrate : AXISDocument
    {
        public int PageSequenceNumber { get; set; }

        public string? PageFilePath { get; set; }

        public Stream FileStream { get; set; }

        public bool HasStreamForDocument { get; set; }

        public string? EmailAttachmentDelimitedString { get; set; }

    }
}
