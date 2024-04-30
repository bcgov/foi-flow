using MCS.FOI.AXISIntegration.DataModels;
using Microsoft.Extensions.Logging;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using Newtonsoft.Json;

namespace MCS.FOI.AXISIntegration.DAL.UnitTests
{

    [TestClass]
    public class RequestDAUnitTest
    {

        private readonly Mock<ILogger<RequestsDA>> _mockLogger = new();

        [TestMethod]
        public void GetRequestTest()
        {
            RequestsDA requestsDA = new(_mockLogger.Object);
            string jsonData = requestsDA.GetAXISRequestString("EDU-2015-50012");
            /*
             "axisRequestId":null,"axisSyncDate":null,"description":null
             */

            AXISRequest deserializedRequest = JsonConvert.DeserializeObject<AXISRequest>(jsonData);
            var axisRequestId = deserializedRequest.AXISRequestID;
            var axisSyncData = deserializedRequest.AxisSyncDate;
            var description = deserializedRequest.RequestDescription;

            Assert.AreEqual(axisRequestId, "EDU-2015-50012");
            Assert.IsNotNull(axisSyncData);
            Assert.IsNotNull(description);
        }

        [TestMethod]
        public void GetNullRequestTest()
        {
            RequestsDA requestsDA = new(_mockLogger.Object);
            string jsonData = requestsDA.GetAXISRequestString("IAP-2015-50012");

            AXISRequest deserializedRequest = JsonConvert.DeserializeObject<AXISRequest>(jsonData);
            var axisRequestId = deserializedRequest.AXISRequestID;
            var axisSyncData = deserializedRequest.AxisSyncDate;
            var description = deserializedRequest.RequestDescription;

            Assert.IsNull(axisRequestId);
            Assert.IsNull(axisSyncData);
            Assert.IsNull(description);
        }

    }
}
