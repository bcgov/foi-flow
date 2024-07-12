using FOIMOD.CFD.DocMigration.FOIFLOW.DAL;
using FOIMOD.HistoricalDocMigration.Models;
using FOIMOD.HistoricalDocMigration.Models.FOIFLOWDestination;
using Microsoft.Extensions.Configuration;
using System.Data.Odbc;

namespace FOIMOD.HistoricalDocMigration.FOIMOD.DAL.Tests
{
    [TestClass]
    public class HistoricalRecordsTests
    {
        [TestInitialize]
        public void HistoricalRecordsTestsInit()
        {
            var configurationbuilder = new ConfigurationBuilder()
                        .AddJsonFile($"appsettings.json", true, true)
                        .AddEnvironmentVariables().Build();

            SystemSettings.FOIFLOWConnectionString = configurationbuilder.GetSection("FOIFLOWConfiguration:FOIFLOWConnectionString").Value;


           
        }


        [TestMethod]
        public void InsertHistoricRecordsTest()
        {
            OdbcConnection connection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
            HistoricalRecordsDAL historicalRecordsDAL = new HistoricalRecordsDAL(connection);
            var result = historicalRecordsDAL.InsertIntoHistoricalRecords(new HistoricalRecords()
            { RecordFileName = "UNITTESTFILENAME", Description = "TEST DESC", AXISRequestID = "UNITTEST- AXIS REQID", CreatedBy = "TEST", IsCorrenpondenceDocument = true, S3Path = "S3 URL PATH" });
            Assert.IsNotNull(result);
        }
    }
}