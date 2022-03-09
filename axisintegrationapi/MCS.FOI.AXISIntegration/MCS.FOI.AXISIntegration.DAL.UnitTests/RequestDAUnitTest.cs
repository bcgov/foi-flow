using Microsoft.Extensions.Logging;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;

namespace MCS.FOI.AXISIntegration.DAL.UnitTests
{

    [TestClass]
    public class RequestDAUnitTest
    {

        private Mock<ILogger> _mockLogger = new Mock<ILogger>();

        [TestMethod]
        public void GetRequestTest()
        {
            RequestsDA requestsDA = new RequestsDA(_mockLogger.Object);
            requestsDA.GetAXISRequestString("Sample");
        }

    }
}
