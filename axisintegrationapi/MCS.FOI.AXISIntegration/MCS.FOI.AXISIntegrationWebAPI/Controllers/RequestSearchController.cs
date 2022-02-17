using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MCS.FOI.AXISIntegrationWebAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
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
        public IEnumerable<AXISRequest> Get()
        {
            _requestDA.GetAXISRequest("REQUEST#");

            var rng = new Random();
            return Enumerable.Range(1, 5).Select(index => new AXISRequest()
            {
                AXISRequestID = "EDUC-2021-4524"
            })
            .ToArray();
        }
    }
}
