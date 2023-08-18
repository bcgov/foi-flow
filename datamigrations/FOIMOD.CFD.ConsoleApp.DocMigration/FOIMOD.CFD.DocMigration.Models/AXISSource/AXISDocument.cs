using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FOIMOD.CFD.DocMigration.Models.AXISSource
{
    public class AXISDocument
    {
        public string? AXISRequestNumber { get; set; }
        public string UNCRootFolder { get; set; }

        public int  IDocID { get; set; }

        public string SiFolderID { get; set; }

        public string TotalPageCount { get; set; }

        public DocumentTypeFromAXIS DocumentType { get; set; }

        public string? EmailContent { get; set; }

        public string? EmailDate { get; set; }

        public string? EmailTo { get; set; }

        public string? EmailFrom { get; set; }
        public string? EmailSubject { get; set; }
    }

    public enum DocumentTypeFromAXIS
    {
        CorrespondenceLog = 0,
        RequestRecords=1, 
    }
}
