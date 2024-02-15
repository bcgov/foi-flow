using Amazon.Runtime.Internal.Util;
using Amazon.S3;
using FOIMOD.CFD.DocMigration.DAL;
using FOIMOD.CFD.DocMigration.FOIFLOW.DAL;
using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
using FOIMOD.CFD.DocMigration.Models.FOIFLOWDestination;
using FOIMOD.CFD.DocMigration.Utils;
using MCS.FOI.OCRtoPDF;
using Microsoft.Data.SqlClient;
using System.Data;
using System.Data.Odbc;
using System.Net.Mail;
using ILogger = Microsoft.Extensions.Logging.ILogger;

namespace FOIMOD.CFD.DocMigration.BAL
{
    public class CorrespondenceLogMigration
    {
        private IDbConnection sourceaxisSQLConnection;
        private IDbConnection destinationfoiflowQLConnection;
        private IAmazonS3 amazonS3;
        private ILogger ilogger;


        public string RequestsToMigrate { get; set; }
        public CorrespondenceLogMigration(IDbConnection _sourceAXISConnection, IDbConnection _destinationFOIFLOWDB, IAmazonS3 _amazonS3,ILogger _logger)
        {
            sourceaxisSQLConnection = _sourceAXISConnection;
            destinationfoiflowQLConnection = _destinationFOIFLOWDB;
            amazonS3 = _amazonS3;
            ilogger = _logger;
        }

        public async Task RunMigration()
        {
            DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3);

            DocumentsDAL documentsDAL = new DocumentsDAL((SqlConnection)sourceaxisSQLConnection);
            AttachmentsDAL attachmentsDAL = new AttachmentsDAL((OdbcConnection)destinationfoiflowQLConnection);
            DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher();
           


            if (SystemSettings.CorrespondenceLogMigration)
            {
                List<DocumentToMigrate>? correspondencelogs = documentsDAL.GetCorrespondenceLogDocuments(this.RequestsToMigrate);
                Console.WriteLine("Starting Migration of Correspondence logs.... ");

                foreach (DocumentToMigrate attachment in correspondencelogs)
                {
                    if (string.IsNullOrEmpty(attachment.EmailTo) && string.IsNullOrEmpty(attachment.EmailContent) && !string.IsNullOrEmpty(attachment.EmailAttachmentDelimitedString))
                    {
                        var files = FilePathUtils.GetFileDetailsFromdelimitedstring(attachment.EmailAttachmentDelimitedString);
                        foreach (var file in files)
                        {
                            //NOT AN EMAIL UPLOAD - DIRECT FILE UPLOAD  - For e.g. https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests-e/Misc/CFD-2023-22081302/applicant/00b8ad71-5d11-4624-9c12-839193cf4a7e.docx
                            var UNCFileLocation = Path.Combine(SystemSettings.FileServerRoot, SystemSettings.CorrespondenceLogBaseFolder, file.FilePathOnServer.Trim());
                            //var UNCFileLocation = file.FileExtension == "pdf" ? @"\\DESKTOP-U67UC02\ioashare\db7e84e1-4202-4837-b4dd-49af233ae006.pdf" : @"\\DESKTOP-U67UC02\ioashare\DOCX1.docx";


                            using (FileStream fs = File.Open(UNCFileLocation, FileMode.Open))
                            {
                                var s3filesubpath = string.Format("{0}/{1}/{2}", SystemSettings.S3_Attachements_BasePath, attachment.AXISRequestNumber, SystemSettings.AttachmentTag);
                                var destinationfilename = string.Format("{0}.{1}", Guid.NewGuid().ToString(), file.FileExtension);
                                var uploadresponse = await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = attachment.AXISRequestNumber.ToUpper(), SubFolderPath = s3filesubpath, DestinationFileName = destinationfilename, FileStream = fs });
                                var fullfileurl = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename);
                                if (uploadresponse.IsSuccessStatusCode)
                                {
                                    //INSERT INTO TABLE - FOIMinistryRequestDocuments
                                    attachmentsDAL.InsertIntoMinistryRequestDocuments(fullfileurl, file.FileName, attachment.AXISRequestNumber);

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
                                        var s3filesubpath = string.Format("{0}/{1}/{2}", SystemSettings.S3_Attachements_BasePath, attachment.AXISRequestNumber, SystemSettings.AttachmentTag);
                                        var destinationfilename = string.Format("{0}.{1}", Guid.NewGuid().ToString(), file.FileExtension);
                                        var uploadresponse = await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = attachment.AXISRequestNumber.ToUpper(), SubFolderPath = s3filesubpath, DestinationFileName = destinationfilename, FileStream = fs });
                                        var fullfileurl = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename);
                                        if (uploadresponse.IsSuccessStatusCode)
                                        {
                                            //INSERT INTO TABLE - FOIMinistryRequestDocuments
                                            attachmentsDAL.InsertIntoMinistryRequestDocuments(fullfileurl, file.FileName, attachment.AXISRequestNumber);

                                        }

                                    }
                                }
                            }
                        }


                        using (Stream emailmessagepdfstream = docMigrationPDFStitcher.MergePDFs(documentToMigrateEmail))
                        {
                            var s3filesubpath = string.Format("{0}/{1}/{2}", SystemSettings.S3_Attachements_BasePath, attachment.AXISRequestNumber, SystemSettings.AttachmentTag);
                            var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());
                            var uploadresponse = await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = attachment.AXISRequestNumber.ToUpper(), SubFolderPath = s3filesubpath, DestinationFileName = destinationfilename, FileStream = emailmessagepdfstream });
                            var fullfileurl = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename);
                            if (uploadresponse.IsSuccessStatusCode)
                            {
                                //INSERT INTO TABLE - FOIMinistryRequestDocuments
                                attachmentsDAL.InsertIntoMinistryRequestDocuments(fullfileurl, string.Format("{0}.pdf", attachment.EmailSubject), attachment.AXISRequestNumber);

                            }
                        }

                    }
                }

                Console.WriteLine("Completed : Migration Correspondence logs.... ");
            }

           


        }

    }
}