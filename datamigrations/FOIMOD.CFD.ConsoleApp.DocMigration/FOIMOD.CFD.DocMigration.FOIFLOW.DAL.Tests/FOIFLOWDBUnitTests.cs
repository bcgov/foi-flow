using FOIMOD.CFD.DocMigration.Models;
using Microsoft.Extensions.Configuration;
using System.Data.Odbc;
using System.Net;
using FOIMOD.CFD.DocMigration.FOIFLOW.DAL;
using static System.Runtime.InteropServices.JavaScript.JSType;
using System;
using System.Xml.Linq;
namespace FOIMOD.CFD.DocMigration.FOIFLOW.DAL.Tests
{
    [TestClass]
    public class FOIFLOWDBUnitTests
    {

        [TestInitialize]
        public void FOIFLOWDBUnitTestInit()
        {
            var configurationbuilder = new ConfigurationBuilder()
                        .AddJsonFile($"appsettings.json", true, true)
                        .AddEnvironmentVariables().Build();

            SystemSettings.FOIFLOWConnectionString = configurationbuilder.GetSection("FOIFLOWConfiguration:FOIFLOWConnectionString").Value;


            SystemSettings.FOIDocReviewerConnectionString = configurationbuilder.GetSection("FOIFLOWConfiguration:FOIDocumentReviewerString").Value;
        }


        [TestMethod]
        public void AttachmentInsertTest()
        {
            OdbcConnection connection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
            AttachmentsDAL attachmentsDAL = new AttachmentsDAL(connection);
            var result = attachmentsDAL.InsertIntoMinistryRequestDocuments("https://unittest", "unittestfile.docx", "CFD-2023-22081302");
            Assert.IsNotNull(result);


        }

        [TestMethod]
        public void GetMinistryRequestDetails()
        {
            try
            {

                OdbcConnection connection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
                OdbcConnection docreviewerconnection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
                RecordsDAL recordsDAL = new RecordsDAL(connection, docreviewerconnection);
                

                var result = recordsDAL.GetMinistryRequestDetails("CFD-2023-0111114711");
                Assert.IsNotNull(result);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

        }

        [TestMethod]
        public void RecordsInsertTest()
        {
            try
            {

                OdbcConnection connection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
                OdbcConnection docreviewerconnection = new OdbcConnection(SystemSettings.FOIDocReviewerConnectionString);

                var s3url = "https://unittest";


                RecordsDAL recordsDAL = new RecordsDAL(connection, docreviewerconnection);
                var minitryrequestdetails = recordsDAL.GetMinistryRequestDetails("CFD-2023-0111114711");


                string attributesJSONtemplate = @"{{""divisions"": [{{""divisionid"": {0}}}], ""lastmodified"": ""{1}"", ""filesize"": {2}, ""batch"": ""{3}"", ""extension"": "".pdf"", ""incompatible"": false}}";
                var attributedJSON = string.Format(attributesJSONtemplate, 422, DateTime.Now.ToString("MM-dd-yyy"), 1803, Guid.NewGuid().ToString());

                var recordid = recordsDAL.InsertIntoFOIRequestRecords("CFD-2023-0111114711", s3url, "unittestfile.pdf", attributedJSON, minitryrequestdetails.Item1,minitryrequestdetails.Item2);

                Assert.IsTrue(recordid != -1 );

                var documentmasterid =   recordsDAL.InsertIntoDocumentMaster(minitryrequestdetails.Item1, s3url, recordid);

                Assert.IsTrue(documentmasterid != -1);

            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

        }
    }
}