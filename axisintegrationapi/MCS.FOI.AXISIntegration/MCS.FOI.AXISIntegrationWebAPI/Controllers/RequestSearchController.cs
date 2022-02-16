using MCS.FOI.AXISIntegrationWebAPI.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace MCS.FOI.AXISIntegrationWebAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class RequestSearchController : ControllerBase
    {

        private readonly ILogger<RequestSearchController> _logger;

       

        public RequestSearchController(ILogger<RequestSearchController> logger)
        {
            _logger = logger;
        }

        [HttpGet]
        public IEnumerable<AXISRequest> Get()
        {
            var rng = new Random();
            return Enumerable.Range(1, 5).Select(index => new AXISRequest()
            {
                AXISRequestID = "EDUC-2021-4524"
            })
            .ToArray();
        }
    }
}
