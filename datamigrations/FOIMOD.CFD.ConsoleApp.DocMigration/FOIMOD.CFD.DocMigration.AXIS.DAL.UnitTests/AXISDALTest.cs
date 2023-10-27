using FOIMOD.CFD.DocMigration.DAL;
using FOIMOD.CFD.DocMigration.Models;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;
namespace FOIMOD.CFD.DocMigration.AXIS.DAL.UnitTests
{
    [TestClass]
    public class AXISDALTest
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
        public void GetCorrespondenceLogDocsTest()
        {
            
            DocumentsDAL documentsDAL = new DocumentsDAL(conn);
            var correspondencelogs = documentsDAL.GetCorrespondenceLogDocuments(requeststomigrate);
            Assert.IsNotNull(correspondencelogs);
            
        }


        [TestMethod]
        public void GetRecordsTest()
        {

            DocumentsDAL documentsDAL = new DocumentsDAL(conn);
            var correspondencelogs = documentsDAL.GetRecordsByRequest("NGD-2015-50137");
            Assert.IsNotNull(correspondencelogs);

        }
    }
}