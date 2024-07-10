using FOIMOD.HistoricalDocMigration.AXIS.DAL;
using FOIMOD.HistoricalDocMigration.Models;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;
namespace FOIMOD.HistoricalDocumentMigration.AXIS.DAL.Tests
{
    [TestClass]
    public class DocumentDALTests
    {


        SqlConnection conn = null;
        string requeststomigrate = String.Empty;
        [TestInitialize]
        public void AXISDALTestInit()
        {
            var configurationbuilder = new ConfigurationBuilder()
                        .AddJsonFile($"appsettings.json", true, true)
                        .AddEnvironmentVariables().Build();

            SystemSettings.AXISConnectionString = configurationbuilder.GetSection("AXISConfiguration:SQLConnectionString").Value;
            SystemSettings.RequestToMigrate = configurationbuilder.GetSection("AXISConfiguration:RequestToMigrate").Value;

            conn = new SqlConnection(SystemSettings.AXISConnectionString);
            requeststomigrate = SystemSettings.RequestToMigrate;

        }




        [TestMethod]
        public void CorrespondenceLogTest()
        {
            DocumentsDAL documentsDAL = new DocumentsDAL(conn);
            var correspondencelogs = documentsDAL.GetCorrespondenceLogDocuments(requeststomigrate);
            Assert.IsNotNull(correspondencelogs);
        }

        [TestMethod]
        public void GetRecordsTest()
        {

            DocumentsDAL documentsDAL = new DocumentsDAL(conn);
            var requestfolderdocuments = documentsDAL.GetRecordsByRequest("ECC-2024-00016");
            Assert.IsNotNull(requestfolderdocuments);

        }
    }
}