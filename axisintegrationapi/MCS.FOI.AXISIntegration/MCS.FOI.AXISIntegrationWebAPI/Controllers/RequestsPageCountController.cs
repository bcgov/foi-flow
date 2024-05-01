using MCS.FOI.AXISIntegration.DAL.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

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

        [HttpPost]

        public ActionResult<string> Post([FromBody] List<string> axisRequestIds)
        {
            try
            {
                if (axisRequestIds == null || axisRequestIds.Count == 0)
                {
                    return BadRequest("The list of axisRequestIds is required.");
                }
                foreach (var requestId in axisRequestIds)
                {
                    if (!IsValidRequestId(requestId))
                    {
                        return BadRequest($"Invalid axisRequestId: {requestId}");
                    }

                    if (ContainsSqlInjectionPattern(requestId))
                    {
                        return BadRequest($"Potential SQL injection detected in axisRequestId: {requestId}");
                    }
                }
                return _requestDA.PostAXISRequestsPageCountString(axisRequestIds.ToArray());

            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, string.Format($"Exception happened on RequestspageCount POST operations, Error Message : {ex.Message} , Stack Trace :{ex.StackTrace}"));
                return string.Format($"Exception happened on RequestspageCount POST operations, Error Message : {ex.Message}");
            }

        }
        private bool IsValidRequestId(string requestId)
        {
            // RequestID should have letters-numbers-numbers format
            string pattern = @"^[A-Za-z]+(?:[-]){0,2}\d+\-\d+$";
            return Regex.IsMatch(requestId, pattern);
        }

        private bool ContainsSqlInjectionPattern(string input)
        {
            string pattern = @"(?:\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b|\b(?:UNION\s+ALL|SELECT\s+.*?\s+FROM\s+.*?\s+WHERE\s+.*?))";
            return Regex.IsMatch(input, pattern, RegexOptions.IgnoreCase);
        }
    }
}
