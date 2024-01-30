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
        public void RecordsInsertTest()
        {
            try
            {

                OdbcConnection connection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
                RecordsDAL recordsDAL = new RecordsDAL(connection);
                string attributesJSONtemplate = @"{{""divisions"": [{{""divisionid"": {0}}}], ""lastmodified"": ""{1}"", ""filesize"": {2}, ""batch"": ""{3}"", ""extension"": "".pdf"", ""incompatible"": false}}";
                var attributedJSON = string.Format(attributesJSONtemplate, 422, DateTime.Now.ToString("MM-dd-yyy"), 1803, Guid.NewGuid().ToString());

                var result = recordsDAL.InsertIntoFOIRequestRecords("CFD-2023-0111114711", "https://unittest", "unittestfile.pdf", attributedJSON);
                Assert.IsNotNull(result);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

        }
    }
}