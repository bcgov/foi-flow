using MCS.FOI.AXISIntegration.DAL;
using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MCS.FOI.AXISIntegrationWebAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [EnableCors(PolicyName = "FOIOrigins")]
    [Authorize]
    public class RequestsPageCountController : ControllerBase
    {

        private readonly ILogger<RequestsPageCountController> _logger;
        private readonly IRequestDA _requestDA;

        public RequestsPageCountController(ILogger<RequestsPageCountController> logger, IRequestDA requestDA)
        {
            _logger = logger;
            _requestDA = requestDA;
        }


        [HttpGet]

        public ActionResult<string> Get()
        {
            try
            {
                
                return _requestDA.GetAXISRequestsPageCountString();

            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, string.Format($"Exception happened on RequestspageCount GET operations, Error Message : {ex.Message} , Stack Trace :{ex.StackTrace}"));
                return string.Format($"Exception happened on RequestspageCount GET operations, Error Message : {ex.Message}");
            }

        }
        [HttpPost]

        public ActionResult<string> Post([FromBody] List<string> axisRequestIds)
        {
            try
            {
                return _requestDA.PostAXISRequestsPageCountString(axisRequestIds.ToArray());

            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, string.Format($"Exception happened on RequestspageCount POST operations, Error Message : {ex.Message} , Stack Trace :{ex.StackTrace}"));
                return string.Format($"Exception happened on RequestspageCount POST operations, Error Message : {ex.Message}");
            }

        }
    }
}
