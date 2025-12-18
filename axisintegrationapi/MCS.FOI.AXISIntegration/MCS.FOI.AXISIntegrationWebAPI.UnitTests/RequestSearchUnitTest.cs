using Microsoft.Extensions.Configuration;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Configuration;
using System.Net.Http;
using System.Net.Http.Headers;

namespace MCS.FOI.AXISIntegrationWebAPI.UnitTests
{
    [TestClass]
    public class RequestSearchUnitTest
    {
        Configuration configuration;
        [TestInitialize]
        public void Init()
        {
            configuration = ConfigurationManager.OpenExeConfiguration(@"MCS.FOI.AXISIntegrationWebAPI.UnitTests.dll");

        }


        [TestMethod]
        public  void GetRequestSuccessfullTest()
        {          
            var apiendpoint = configuration.AppSettings.Settings["TESTAPiENDPOINT"].Value;
            var validtoken = configuration.AppSettings.Settings["VALIDLIVEBEARERTOKEN"].Value; 
            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", validtoken);
            HttpResponseMessage response =  httpClient.GetAsync(apiendpoint).Result;
            Assert.AreEqual(response.EnsureSuccessStatusCode().StatusCode,System.Net.HttpStatusCode.OK);
        }

        [TestMethod]
        public void GetRequestUnSuccessfullTest()
        {
            var apiendpoint = configuration.AppSettings.Settings["TESTAPiENDPOINT"].Value;            
            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "____INVALIDTOKENFORFALSECONDITIONCHECK______");
            HttpResponseMessage response = httpClient.GetAsync(apiendpoint).Result;            
            Assert.AreEqual(response.IsSuccessStatusCode, false);
        }
    }
}
