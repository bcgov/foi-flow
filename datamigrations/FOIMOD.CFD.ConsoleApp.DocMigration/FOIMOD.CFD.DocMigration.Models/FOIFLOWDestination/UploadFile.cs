using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FOIMOD.CFD.DocMigration.Models.FOIFLOWDestination
{
    public class UploadFile
    {

        public string SourceFileName { get; set; }

        public string DestinationFileName { get; set; }

        public string AXISRequestID { get; set; }

        public string SubFolderPath { get; set; }

        public UploadType UploadType { get; set; }

        public string S3BucketName { get; set; }

      

        public Stream FileStream { get; set; }
    }

    public enum UploadType
    {
        Attachments = 1,
            Records = 2

    }


}
