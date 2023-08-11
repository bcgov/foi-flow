

using Amazon.Runtime;
using Amazon.S3;
using Amazon.S3.Model;
using Microsoft.VisualStudio.TestPlatform.Utilities;
using System.Buffers.Text;

namespace FOIMOD.CFD.DocMigration.Utils.UnitTests
{
    [TestClass]
    public class S3UploadTest
    {
        [TestMethod]
        public   void S3Upload_UploadFileAsync()
        {
            string baseA = AppDomain.CurrentDomain.SetupInformation.ApplicationBase;
            string testfile =  System.IO.Directory.GetParent(baseA).Parent.FullName;
            
            AWSCredentials s3credentials  = new BasicAWSCredentials("", "");
            AmazonS3Config config = new()
            {
                ServiceURL = "https://citz-foi-prod.objectstore.gov.bc.ca/"
            };
            AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);
           
            DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3Client);


            using var client = new HttpClient();
            using (FileStream fs = File.Open(Path.Combine(getSourceFolder(),"DOCX1.pdf"), FileMode.Open))
            {
                fs.Position = 0;
                var destinationfilename = string.Format("{0}.pdf",  Guid.NewGuid().ToString());
                
                UploadFile uploadFile = new UploadFile() { ContentType="application/pdf", AXISRequestID = "TEST-10001-12342", DestinationFileName = destinationfilename, S3BucketName = "test123-protected", SubFolderPath = "test123-protected/Abintest/unittestmigration", UploadType = UploadType.Attachments, SourceFileName = "DOC1.pdf", FileStream = fs };
                var result = docMigrationS3Client.UploadFileAsync(uploadFile).Result;
            }
        }

        private string getSourceFolder()
        {
            return "C:\\AOT\\FOI\\Source\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.Utils.UnitTests\\samples\\";
        }


    }
}