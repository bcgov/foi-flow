using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
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
    [EnableCors]
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
                return _requestDA.GetAXISRequestString(requestNumber);
            }
            catch(Exception ex)
            {
                return ex.Message;
            }
            
        }
    }
}
