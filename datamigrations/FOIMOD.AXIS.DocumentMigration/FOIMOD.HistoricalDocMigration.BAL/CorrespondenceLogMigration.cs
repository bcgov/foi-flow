using Amazon.S3;
using FOIMOD.HistoricalDocMigration.AXIS.DAL;
using FOIMOD.HistoricalDocMigration.DocMigration.FOIFLOW.DAL;
using FOIMOD.HistoricalDocMigration.Models;
using FOIMOD.HistoricalDocMigration.Models.Document;
using FOIMOD.HistoricalDocMigration.Models.FOIFLOWDestination;
using FOIMOD.HistoricalDocMigration.Utils;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Logging;
using System.Data;
using System.Data.Odbc;
using ILogger = Microsoft.Extensions.Logging.ILogger;


namespace FOIMOD.HistoricalDocMigration.DocMigration.BAL
{
    public class CorrespondenceLogMigration
    {
        private IDbConnection sourceaxisSQLConnection;
        private IDbConnection destinationfoiflowQLConnection;
        private IAmazonS3 amazonS3;
        private ILogger ilogger;


        public string RequestsToMigrate { get; set; }
        public CorrespondenceLogMigration(IDbConnection _sourceAXISConnection, IDbConnection _destinationFOIFLOWDB, IAmazonS3 _amazonS3, ILogger _logger)
        {
            sourceaxisSQLConnection = _sourceAXISConnection;
            destinationfoiflowQLConnection = _destinationFOIFLOWDB;
            amazonS3 = _amazonS3;
            ilogger = _logger;
        }

        public async Task RunMigration()
        {
            try
            {
                DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3);

                DocumentsDAL documentsDAL = new DocumentsDAL((SqlConnection)sourceaxisSQLConnection);
                HistoricalRecordsDAL attachmentsDAL = new HistoricalRecordsDAL((OdbcConnection)destinationfoiflowQLConnection);
                DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher();



                if (SystemSettings.CorrespondenceLogMigration)
                {
                    Console.WriteLine("Starting Migration of Correspondence logs.... ");

                    var requestsArray = this.RequestsToMigrate.Split(",");

                    foreach (var _requestID in requestsArray)
                    {
                        List<DocumentToMigrate>? correspondencelogs = documentsDAL.GetCorrespondenceLogDocuments(_requestID);


                        foreach (DocumentToMigrate attachment in correspondencelogs)
                        {
                            try
                            {
                                var year = attachment.ClosingDate.Value.Year;
                                var month = attachment.ClosingDate.Value.Month;

                                if (attachment.CLFileType == "CL")
                                {

                                    if (string.IsNullOrEmpty(attachment.EmailTo) && string.IsNullOrEmpty(attachment.EmailContent) && !string.IsNullOrEmpty(attachment.EmailAttachmentDelimitedString) && attachment.ClosingDate != null)
                                    {
                                        var files = FilePathUtils.GetFileDetailsFromdelimitedstring(attachment.EmailAttachmentDelimitedString);




                                        foreach (var file in files)
                                        {
                                            //NOT AN EMAIL UPLOAD - DIRECT FILE UPLOAD  - For e.g. https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests-e/Misc/CFD-2023-22081302/applicant/00b8ad71-5d11-4624-9c12-839193cf4a7e.docx
                                            var UNCFileLocation = Path.Combine(SystemSettings.FileServerRoot, SystemSettings.CorrespondenceLogBaseFolder, file.FilePathOnServer.Trim());
                                            //var UNCFileLocation = file.FileExtension == "pdf" ? @"\\DESKTOP-U67UC02\ioashare\db7e84e1-4202-4837-b4dd-49af233ae006.pdf" : @"\\DESKTOP-U67UC02\ioashare\DOCX1.docx";


                                            using (FileStream fs = File.Open(UNCFileLocation, FileMode.Open))
                                            {

                                                var s3filesubpath = string.Format("{0}/{1}/{2}/{3}/{4}", SystemSettings.S3_Attachements_BasePath, "CL", year, month, attachment.AXISRequestNumber);
                                                var destinationfilename = string.Format("{0}.{1}", Guid.NewGuid().ToString(), file.FileExtension);
                                                var filename = FilePathUtils.CleanFileNameInput(file.FileName);
                                                var historicalcorrespondencelog = new HistoricalRecords() { AXISRequestID = attachment.AXISRequestNumber.ToUpper(), S3Subfolder = s3filesubpath, S3Path = s3filesubpath, RecordFileName = destinationfilename, FileStream = fs, IsCorrenpondenceDocument = true, DisplayFileName = filename };
                                                var uploadresponse = await docMigrationS3Client.UploadFileAsync(historicalcorrespondencelog);
                                                var fullfileurl = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename);
                                                if (uploadresponse.IsSuccessStatusCode)
                                                {
                                                    //INSERT INTO Historical table
                                                    attachmentsDAL.InsertIntoHistoricalRecords(historicalcorrespondencelog);

                                                }

                                            }

                                        }

                                    }
                                    else
                                    {
                                        //Create EMAIL MSG PDF and sticth with the attachment documents
                                        List<DocumentToMigrate> documentToMigrateEmail = new List<DocumentToMigrate>();
                                        var attachmentfiles = FilePathUtils.GetFileDetailsFromdelimitedstring(attachment.EmailAttachmentDelimitedString);
                                        using var emaildocstream = docMigrationPDFStitcher.CreatePDFDocument(attachment.EmailContent, attachment.EmailSubject, attachment.EmailDate, attachment.EmailTo, attachmentfiles);
                                        emaildocstream.Position = 0;
                                        documentToMigrateEmail.Add(new DocumentToMigrate() { FileStream = emaildocstream, DocumentType = Models.AXISSource.DocumentTypeFromAXIS.CorrespondenceLog, AXISRequestNumber = attachment.AXISRequestNumber.ToUpper(), PageSequenceNumber = 1, HasStreamForDocument = true });


                                        if (attachmentfiles != null)
                                        {
                                            foreach (var file in attachmentfiles)
                                            {
                                                var UNCFileLocation = Path.Combine(SystemSettings.FileServerRoot, SystemSettings.CorrespondenceLogBaseFolder.Trim(), file.FilePathOnServer?.Trim());
                                                //var UNCFileLocation = file.FileExtension == "pdf" ? @"\\DESKTOP-U67UC02\ioashare\db7e84e1-4202-4837-b4dd-49af233ae006.pdf" : @"\\DESKTOP-U67UC02\ioashare\DOCX1.docx";
                                                if (file.FileExtension == "pdf")
                                                {

                                                    documentToMigrateEmail.Add(new DocumentToMigrate()
                                                    { PageFilePath = UNCFileLocation, PageSequenceNumber = 2 });

                                                }
                                                else
                                                {
                                                    using (FileStream fs = File.Open(UNCFileLocation, FileMode.Open))
                                                    {
                                                        var s3filesubpath = string.Format("{0}/{1}/{2}/{3}/{4}", SystemSettings.S3_Attachements_BasePath, "CL", year, month, attachment.AXISRequestNumber);
                                                        var destinationfilename = string.Format("{0}.{1}", Guid.NewGuid().ToString(), file.FileExtension);
                                                        var filename = FilePathUtils.CleanFileNameInput(file.FileName);
                                                        var historicalcorrespondencelog = new HistoricalRecords() { AXISRequestID = attachment.AXISRequestNumber.ToUpper(), S3Subfolder = s3filesubpath, S3Path = s3filesubpath, RecordFileName = destinationfilename, FileStream = fs, IsCorrenpondenceDocument = true, DisplayFileName = filename };
                                                        var uploadresponse = await docMigrationS3Client.UploadFileAsync(historicalcorrespondencelog);
                                                        var fullfileurl = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename);
                                                        if (uploadresponse.IsSuccessStatusCode)
                                                        {
                                                            //INSERT INTO Historical table
                                                            attachmentsDAL.InsertIntoHistoricalRecords(historicalcorrespondencelog);

                                                        }

                                                    }
                                                }
                                            }
                                        }


                                        using (Stream emailmessagepdfstream = docMigrationPDFStitcher.MergePDFs(documentToMigrateEmail))
                                        {
                                            var s3filesubpath = string.Format("{0}/{1}/{2}/{3}/{4}", SystemSettings.S3_Attachements_BasePath, "CL", year, month, attachment.AXISRequestNumber);
                                            var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());
                                            var filename = string.Format("{0}.pdf", FilePathUtils.CleanFileNameInput(attachment.EmailSubject));
                                            var historicalcorrespondencelog = new HistoricalRecords() { AXISRequestID = attachment.AXISRequestNumber.ToUpper(), S3Subfolder = s3filesubpath, S3Path = s3filesubpath, RecordFileName = destinationfilename, FileStream = emailmessagepdfstream, IsCorrenpondenceDocument = true, DisplayFileName = filename };
                                            var uploadresponse = await docMigrationS3Client.UploadFileAsync(historicalcorrespondencelog);
                                            var fullfileurl = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename);
                                            if (uploadresponse.IsSuccessStatusCode)
                                            {
                                                //INSERT INTO Historical table
                                                attachmentsDAL.InsertIntoHistoricalRecords(historicalcorrespondencelog);

                                            }
                                        }

                                    }
                                }
                                else
                                {
                                    //NOT AN EMAIL UPLOAD - DIRECT FILE UPLOAD  - For e.g. https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests-e/Misc/CFD-2023-22081302/applicant/00b8ad71-5d11-4624-9c12-839193cf4a7e.docx
                                    var UNCFileLocation = Path.Combine(SystemSettings.FileServerRoot, SystemSettings.CorrespondenceLogBaseFolder, attachment.EmailAttachmentDelimitedString.Trim());
                                    //var UNCFileLocation = file.FileExtension == "pdf" ? @"\\DESKTOP-U67UC02\ioashare\db7e84e1-4202-4837-b4dd-49af233ae006.pdf" : @"\\DESKTOP-U67UC02\ioashare\DOCX1.docx";


                                    using (FileStream fs = File.Open(UNCFileLocation, FileMode.Open))
                                    {

                                        var s3filesubpath = string.Format("{0}/{1}/{2}/{3}/{4}", SystemSettings.S3_Attachements_BasePath, "CL", year, month, attachment.AXISRequestNumber);
                                        var destinationfilename = string.Format("{0}.{1}", Guid.NewGuid().ToString(), "zip");
                                        var filename = string.Format("{0}_ResponsePackage.zip", attachment.AXISRequestNumber);
                                        var historicalcorrespondencelog = new HistoricalRecords() { AXISRequestID = attachment.AXISRequestNumber.ToUpper(), S3Subfolder = s3filesubpath, S3Path = s3filesubpath, RecordFileName = destinationfilename, FileStream = fs, IsCorrenpondenceDocument = true, DisplayFileName = filename, Attributes = @"{""ResponsePackage"":""True""}" };
                                        var uploadresponse = await docMigrationS3Client.UploadFileAsync(historicalcorrespondencelog);
                                        var fullfileurl = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename);
                                        if (uploadresponse.IsSuccessStatusCode)
                                        {
                                            //INSERT INTO Historical table
                                            attachmentsDAL.InsertIntoHistoricalRecords(historicalcorrespondencelog);

                                        }

                                    }
                                }
                            }
                            catch (Exception ex)
                            {
                                ilogger.LogError(string.Format("Correspondence Log Migration, Error happened while uploading attachment for request : {0} and error is like, {1}", attachment.AXISRequestNumber, ex.Message));
                            }
                        }
                    }

                   

                    Console.WriteLine("Completed : Migration Correspondence logs.... ");
                }

            }
            catch (Exception e)
            {
                ilogger.LogError(string.Format("Correspondence log migration, Error happened : {0}", e.Message));
            }


        }

    }
}