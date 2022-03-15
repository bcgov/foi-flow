using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MCS.FOI.AXISIntegrationWebAPI.Controllers
{
    [Route("api/[controller]/{requestNumber}")]
    [ApiController]
    [EnableCors(PolicyName = "FOIOrigins")]
    [Authorize(Policy = "IAOTeam")]
    public class RequestSearchController : ControllerBase
    {

        private readonly ILogger<RequestSearchController> _logger;
        private readonly IRequestDA _requestDA;


        public RequestSearchController(ILogger<RequestSearchController> logger, IRequestDA requestDA)
        {
            _logger = logger;
            _requestDA = requestDA;
        }

        [HttpGet]
        
        public string Get(string requestNumber)
        {
            try
            {                
                if (!string.IsNullOrEmpty(requestNumber) && requestNumber.Length > 10)
                    return _requestDA.GetAXISRequestString(requestNumber);
                else
                    return "";
            }
            catch(Exception ex)
            {
                _logger.Log(LogLevel.Error, string.Format($"Exception happened while GET operations of request - {requestNumber}, Error Message : {ex.Message} , Stack Trace :{ex.StackTrace}"));
                return ex.Message;
            }
            
        }
    }
}
