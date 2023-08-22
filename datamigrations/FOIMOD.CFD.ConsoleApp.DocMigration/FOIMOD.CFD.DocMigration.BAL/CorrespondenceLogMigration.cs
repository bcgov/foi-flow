using Amazon.S3;
using FOIMOD.CFD.DocMigration.DAL;
using Microsoft.Data.SqlClient;
using System.Data;
using System.Data.Odbc;
using FOIMOD.CFD.DocMigration.Models.Document;
using FOIMOD.CFD.DocMigration.Models.FOIFLOWDestination;
using FOIMOD.CFD.DocMigration.Utils;

namespace FOIMOD.CFD.DocMigration.BAL
{
    public class CorrespondenceLogMigration
    {
        private IDbConnection sourceaxisSQLConnection;
        private IDbConnection destinationfoiflowQLConnection;
        private IAmazonS3 amazonS3;

        public string RequestsToMigrate { get; set; }
        public CorrespondenceLogMigration(IDbConnection _sourceAXISConnection, IDbConnection _destinationFOIFLOWDB, IAmazonS3 _amazonS3 ) 
        {
            sourceaxisSQLConnection = _sourceAXISConnection;
            destinationfoiflowQLConnection= _destinationFOIFLOWDB;
            amazonS3 = _amazonS3;
        }

        public async Task RunMigration()
        {
            DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3);

            DocumentsDAL documentsDAL = new DocumentsDAL((SqlConnection)sourceaxisSQLConnection);
            List<DocumentToMigrate>? correspondencelogs = documentsDAL.GetCorrespondenceLogDocuments(this.RequestsToMigrate);
            foreach (DocumentToMigrate attachment in correspondencelogs)
            {
                if (string.IsNullOrEmpty(attachment.EmailTo) && string.IsNullOrEmpty(attachment.EmailContent))
                {
                    //NOT AN EMAIL UPLOAD - DIRECT FILE UPLOAD

                   //await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = attachment.AXISRequestNumber , FileStream})
                }
                else
                {
                    //Create EMAIL MSG PDF and sticth with the attachment documents
                }
            }

        }

    }
}