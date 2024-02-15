

using Amazon;
using Amazon.Runtime;
using Amazon.S3;
using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
using Microsoft.Extensions.Configuration;

namespace FOIMOD.CFD.DocMigration.Utils.UnitTests
{
    [TestClass]
    public class S3UploadTest
    {
        public AWSCredentials s3credentials = null;
        public AmazonS3Config config = null;
        [TestInitialize]
        public void S3UploadTestInit()
        {
            var configurationbuilder = new ConfigurationBuilder()
                        .AddJsonFile($"appsettings.dev.json", true, true)
                        .AddEnvironmentVariables().Build();

            SystemSettings.S3_AccessKey = configurationbuilder.GetSection("S3Configuration:AWS_accesskey").Value;
            SystemSettings.S3_SecretKey = configurationbuilder.GetSection("S3Configuration:AWS_secret").Value;
            SystemSettings.S3_EndPoint = configurationbuilder.GetSection("S3Configuration:AWS_S3_Url").Value;

            s3credentials = new BasicAWSCredentials(SystemSettings.S3_AccessKey, SystemSettings.S3_SecretKey);

            config = new()
            {
                ServiceURL = SystemSettings.S3_EndPoint

            };
        }


        [TestMethod]
        public void S3Upload_UploadFileAsync()
        {
            AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);
            DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3Client);

            using var client = new HttpClient();
            using (FileStream fs = File.Open(Path.Combine(getSourceFolder(), "DOCX1.pdf"), FileMode.Open))
            {
                fs.Position = 0;
                var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());

                UploadFile uploadFile = new UploadFile() { AXISRequestID = "TEST-10001-12342", DestinationFileName = destinationfilename, S3BucketName = "test123-protected", SubFolderPath = "test123-protected/Abintest/unittestmigration", UploadType = UploadType.Attachments, SourceFileName = "DOC1.pdf", FileStream = fs };
                var result = docMigrationS3Client.UploadFileAsync(uploadFile).Result;
                Assert.IsNotNull(result);
                Assert.IsTrue(result.IsSuccessStatusCode);
            }
        }

        [TestMethod]
        public void PDFMerge_UploadTest()
        {
            List<DocumentToMigrate> pDFDocToMerges = new List<DocumentToMigrate>();
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "DOCX1.pdf"), PageSequenceNumber = 3 });
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "cat1.pdf"), PageSequenceNumber = 2 });


            using (DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher())
            {
                using Stream fs = docMigrationPDFStitcher.MergePDFs(pDFDocToMerges);

                AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);

                DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3Client);


                using var client = new HttpClient();

                fs.Position = 0;
                var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());

                UploadFile uploadFile = new UploadFile() { AXISRequestID = "TEST-10001-12342", DestinationFileName = destinationfilename, S3BucketName = "test123-protected", SubFolderPath = "test123-protected/Abintest/unittestmigration", UploadType = UploadType.Attachments, SourceFileName = "DOC1.pdf", FileStream = fs };
                var result = docMigrationS3Client.UploadFileAsync(uploadFile).Result;
                Assert.IsNotNull(result);
                Assert.IsTrue(result.IsSuccessStatusCode);

            }
        }


        [TestMethod]
        public void PDFMerge_ProductIssueTest()
        {
            List<DocumentToMigrate> pDFDocToMerges = new List<DocumentToMigrate>();
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "prodfiles\\1.pdf"), PageSequenceNumber = 1 , DocumentType = Models.AXISSource.DocumentTypeFromAXIS.RequestRecords});
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "prodfiles\\2.pdf"), PageSequenceNumber = 2, DocumentType = Models.AXISSource.DocumentTypeFromAXIS.RequestRecords });
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "prodfiles\\3.pdf"), PageSequenceNumber = 3, DocumentType = Models.AXISSource.DocumentTypeFromAXIS.RequestRecords });

            using (DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher())
            {
                using Stream fs = docMigrationPDFStitcher.MergePDFs(pDFDocToMerges);

                AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);

                DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3Client);


                using var client = new HttpClient();

                fs.Position = 0;
                var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());

                UploadFile uploadFile = new UploadFile() { AXISRequestID = "TEST-10001-12342", DestinationFileName = destinationfilename, S3BucketName = "test123-protected", SubFolderPath = "test123-protected/Abintest/unittestmigration", UploadType = UploadType.Attachments, SourceFileName = "DOC1.pdf", FileStream = fs };
                var result = docMigrationS3Client.UploadFileAsync(uploadFile).Result;
                Assert.IsNotNull(result);
                Assert.IsTrue(result.IsSuccessStatusCode);

            }
        }

        [TestMethod]
        public void PNGMerge_UploadTest()
        {
            List<DocumentToMigrate> pDFDocToMerges = new List<DocumentToMigrate>();
            pDFDocToMerges.Add(new DocumentToMigrate() { FileStream = File.OpenRead(Path.Combine(getSourceFolder(), "pngs\\scansample.png")), PageFilePath = Path.Combine(getSourceFolder(), "pngs\\scansample.png"), PageSequenceNumber = 1 });
            pDFDocToMerges.Add(new DocumentToMigrate() { FileStream = File.OpenRead(Path.Combine(getSourceFolder(), "pngs\\scansample2.png")), PageFilePath = Path.Combine(getSourceFolder(), "pngs\\scansample2.png"), PageSequenceNumber = 2 });


            using (DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher())
            {
                using Stream fs = docMigrationPDFStitcher.MergeImages(pDFDocToMerges);

                AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);

                DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3Client);


                using var client = new HttpClient();

                fs.Position = 0;
                var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());

                UploadFile uploadFile = new UploadFile() { AXISRequestID = "TEST-10001-12342", DestinationFileName = destinationfilename, S3BucketName = "test123-protected", SubFolderPath = "test123-protected/Abintest/unittestmigration", UploadType = UploadType.Attachments, SourceFileName = "DOC1.pdf", FileStream = fs };
                var result = docMigrationS3Client.UploadFileAsync(uploadFile).Result;
                Assert.IsNotNull(result);
                Assert.IsTrue(result.IsSuccessStatusCode);

            }
        }

        [TestMethod]

        public void CreatePDF_Test()
        {
            AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);
            DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3Client);
            using (DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher())
            {
                using Stream emaildocstream = docMigrationPDFStitcher.CreatePDFDocument("<p><h1>THIS IS AN EMAIL HTML content</h1></p>", "My email subject line!!!!", DateTime.Now.AddYears(-10).ToLongDateString(), "abinajik@gmail.com");
                emaildocstream.Position = 0;
                var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());
                UploadFile uploadFile = new UploadFile() { AXISRequestID = "TEST-10001-12342", DestinationFileName = destinationfilename, S3BucketName = "test123-protected", SubFolderPath = "test123-protected/Abintest/unittestmigration", UploadType = UploadType.Attachments, SourceFileName = "DOC1.pdf", FileStream = emaildocstream };
                var result = docMigrationS3Client.UploadFileAsync(uploadFile).Result;
                Assert.IsNotNull(result);
                Assert.IsTrue(result.IsSuccessStatusCode);


            }

        }


        [TestMethod]
        public void MergeStreamwithFileAttachmentsTest()
        {
            AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);
            DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3Client);
            using (DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher())
            {
                using Stream emaildocstream = docMigrationPDFStitcher.CreatePDFDocument("<p><h1>THIS IS AN EMAIL HTML content</h1></p>", "My email subject line!!!!", DateTime.Now.AddYears(-10).ToLongDateString(), "abinajik@gmail.com");
                emaildocstream.Position = 0;


                List<DocumentToMigrate> pDFDocToMerges = new List<DocumentToMigrate>();
                pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "DOCX1.pdf"), PageSequenceNumber = 3 });
                pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "cat1.pdf"), PageSequenceNumber = 2 });
                pDFDocToMerges.Add(new DocumentToMigrate() { FileStream = emaildocstream, PageSequenceNumber = 1, HasStreamForDocument = true });

                using Stream fs = docMigrationPDFStitcher.MergePDFs(pDFDocToMerges);

                using var client = new HttpClient();

                fs.Position = 0;
                var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());

                UploadFile uploadFile = new UploadFile() { AXISRequestID = "TEST-10001-12342", DestinationFileName = destinationfilename, S3BucketName = "test123-protected", SubFolderPath = "test123-protected/Abintest/unittestmigration", UploadType = UploadType.Attachments, SourceFileName = "DOC1.pdf", FileStream = fs };
                var result = docMigrationS3Client.UploadFileAsync(uploadFile).Result;
                Assert.IsNotNull(result);
                Assert.IsTrue(result.IsSuccessStatusCode);


            }
        }


        private string getSourceFolder()
        {
            return "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.Utils.UnitTests\\samples\\";
        }


    }
}