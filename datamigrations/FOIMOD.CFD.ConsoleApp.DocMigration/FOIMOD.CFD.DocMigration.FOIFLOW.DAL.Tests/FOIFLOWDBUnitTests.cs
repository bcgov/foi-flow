using FOIMOD.CFD.DocMigration.Models;
using Microsoft.Extensions.Configuration;
using System.Data.Odbc;
using System.Net;
using FOIMOD.CFD.DocMigration.FOIFLOW.DAL;
using static System.Runtime.InteropServices.JavaScript.JSType;
using System;
using System.Xml.Linq;
using FOIMOD.CFD.DocMigration.Utils;
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
        public void GetSectionIDByAxisFolderNameTest()
        {
            try
            {

                OdbcConnection connection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
                OdbcConnection docreviewerconnection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
                RecordsDAL recordsDAL = new RecordsDAL(connection, docreviewerconnection);

                using (AXISFolderToMODSectionUtil aXISFolderToMODSectionUtil =
                new AXISFolderToMODSectionUtil(
                    "C:\\Abindev\\foi-flow\\datamigrations" +
                    "\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.ConsoleApp.DocMigration" +
                    "\\sectionmapping\\axistomodsectionmapping.json"))
                {

                    var resultexactmatch_case0 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("INTAKE, ASSESSMENT & RESPONSE");
                    Assert.AreEqual("INTAKE ASSESSMENT AND RESPONSE", resultexactmatch_case0);
                    int resultsectionoid = recordsDAL.GetSectionIDByName(resultexactmatch_case0);
                    Assert.AreEqual(246, resultsectionoid);
                 
                    var resultexactmatch_case3 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("FS CPF 1-9C8LS_6.1_RappProg_ProgRep");
                    Assert.AreEqual("TBD", resultexactmatch_case3);
                    int resultsectionoid_tbd = recordsDAL.GetSectionIDByName(resultexactmatch_case3);
                    Assert.AreEqual(427, resultsectionoid_tbd);

                    var possiblesectioninlast_case4 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("LAUGHY, Laura-Ann Mae ICM FS Case Report 1-3402-141523");
                    Assert.AreEqual("ICM-FS Case Report", possiblesectioninlast_case4);
                    int resultsectionoid_ICMFSCaseReport = recordsDAL.GetSectionIDByName(possiblesectioninlast_case4);
                    Assert.AreEqual(430, resultsectionoid_ICMFSCaseReport);



                }
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

                var filename = string.Format("unittestfile-{0}.pdf", Guid.NewGuid().ToString().Replace("-", ""));
                var s3url = string.Format("https://unittest/{0}",filename);
                
                int pagecount = 1;
                var documenthash = Guid.NewGuid().ToString().Replace("-", "");
                var batch = Guid.NewGuid().ToString();
                int filesize = 1803;
                var sectiondivisionid = 422;


                RecordsDAL recordsDAL = new RecordsDAL(connection, docreviewerconnection);
                var minitryrequestdetails = recordsDAL.GetMinistryRequestDetails("CFD-2023-0111114711");


                string attributesJSONtemplate = @"{{""divisions"": [{{""divisionid"": {0}}}], ""lastmodified"": ""{1}"", ""filesize"": {2}, ""batch"": ""{3}"", ""extension"": "".pdf"", ""incompatible"": false}}";
                var attributedJSON = string.Format(attributesJSONtemplate, sectiondivisionid, DateTime.Now.ToString("MM-dd-yyy"), filesize, batch);

                var recordid = recordsDAL.InsertIntoFOIRequestRecords("CFD-2023-0111114711", s3url, filename, attributedJSON, minitryrequestdetails.Item1,minitryrequestdetails.Item2);

                Assert.IsTrue(recordid != -1 );

                var documentmasterid =   recordsDAL.InsertIntoDocumentMaster(minitryrequestdetails.Item1, s3url, recordid);

                Assert.IsTrue(documentmasterid != -1);

                var documentid = recordsDAL.InsertIntoDocuments(minitryrequestdetails.Item1, filename, pagecount, documentmasterid);

                Assert.IsTrue(documentid != -1);

               
                var resultAttributes = recordsDAL.InsertIntoDocumentAttributes(documentmasterid, attributedJSON);

                

                var resultInsertIntoDocumentHashcodes = recordsDAL.InsertIntoDocumentHashcodes(documentid, documenthash);

                

                var resultDedupljob = recordsDAL.InsertIntoDeduplicationJob(documentmasterid, minitryrequestdetails.Item1, batch, filename);

              


            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

        }
    }
}