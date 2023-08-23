using Amazon.S3;
using FOIMOD.CFD.DocMigration.DAL;
using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
using FOIMOD.CFD.DocMigration.Models.FOIFLOWDestination;
using FOIMOD.CFD.DocMigration.Utils;
using Microsoft.Data.SqlClient;
using System.Data;

namespace FOIMOD.CFD.DocMigration.BAL
{
    public class CorrespondenceLogMigration
    {
        private IDbConnection sourceaxisSQLConnection;
        private IDbConnection destinationfoiflowQLConnection;
        private IAmazonS3 amazonS3;

        public string RequestsToMigrate { get; set; }
        public CorrespondenceLogMigration(IDbConnection _sourceAXISConnection, IDbConnection _destinationFOIFLOWDB, IAmazonS3 _amazonS3)
        {
            sourceaxisSQLConnection = _sourceAXISConnection;
            destinationfoiflowQLConnection = _destinationFOIFLOWDB;
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
                    var files = FilePathUtils.GetFileDetailsFromdelimitedstring(attachment.EmailAttachmentDelimitedString);
                    foreach (var file in files)
                    {
                        //NOT AN EMAIL UPLOAD - DIRECT FILE UPLOAD  - For e.g. https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests-e/Misc/CFD-2023-22081302/applicant/00b8ad71-5d11-4624-9c12-839193cf4a7e.docx
                        var UNCFileLocation = Path.Combine(SystemSettings.FileServerRoot, SystemSettings.CorrespondenceLogBaseFolder, file.FilePathOnServer);
                        //var UNCFileLocation = file.FileExtension == "pdf" ? @"\\DESKTOP-U67UC02\ioashare\db7e84e1-4202-4837-b4dd-49af233ae006.pdf" : @"\\DESKTOP-U67UC02\ioashare\DOCX1.docx";
                        

                        using (FileStream fs = File.Open(UNCFileLocation, FileMode.Open))                        
                        {
                            var s3filesubpath = string.Format("{0}/{1}/{2}", SystemSettings.S3_Attachements_BasePath, attachment.AXISRequestNumber, SystemSettings.AttachmentTag);
                            
                            await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = attachment.AXISRequestNumber.ToUpper(), SubFolderPath = s3filesubpath, DestinationFileName = string.Format("{0}.{1}", Guid.NewGuid().ToString(), file.FileExtension), FileStream =fs});

                        }

                    }

                }
                else
                {
                    //Create EMAIL MSG PDF and sticth with the attachment documents
                }
            }

        }

    }
}