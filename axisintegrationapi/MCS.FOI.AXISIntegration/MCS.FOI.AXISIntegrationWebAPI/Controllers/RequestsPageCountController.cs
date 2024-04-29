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
                string[] requestIds = new string[] { "EMP-2019-96623", "XGR-2019-93646" };
                return _requestDA.GetAXISRequestsPageCountString(requestIds);

            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, string.Format($"Exception happened on RequestspageCount GET operations, Error Message : {ex.Message} , Stack Trace :{ex.StackTrace}"));
                return string.Format($"Exception happened on RequestspageCount GET operations, Error Message : {ex.Message}");
            }

        }
    }
}
