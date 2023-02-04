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
    [Route("api/[controller]/{requestNumber}/{type}/{id}")]
    [ApiController]
    [EnableCors(PolicyName = "FOIOrigins")]
    [Authorize(Policy = "IAOTeam")]
    public class RequestSearchController : ControllerBase
    {

        private readonly ILogger<RequestSearchController> _logger;
        private readonly IRequestDA _requestDA;
        private readonly IFOIFlowRequestUserDA _fOIFlowRequestUser;

        public RequestSearchController(ILogger<RequestSearchController> logger, IRequestDA requestDA, IFOIFlowRequestUserDA fOIFlowRequestUser)
        {
            _logger = logger;
            _requestDA = requestDA;
            _fOIFlowRequestUser = fOIFlowRequestUser;
        }

        [HttpGet]

        public string Get(string requestNumber, string type, int id)
        {
            try
            {
                var isIAORestrictedRequestManager = User.HasClaim(claim => claim.Value == "/IAO Restricted Files Manager" && claim.Type == "groups");
                var isassigneeorwatcher = false;
                

                if (!isIAORestrictedRequestManager)
                {
                    var users = _fOIFlowRequestUser.GetAssigneesandWatchers(id, type);
                    foreach (var user in users)
                    {
                        isassigneeorwatcher =  User.HasClaim(claim => claim.Value.ToUpper() == user.username.ToUpper().Replace("@IDIR","") && claim.Type == "foi_preferred_username");
                        if (isassigneeorwatcher)
                        {
                            break;
                        }
                    }
                }

                if (!string.IsNullOrEmpty(requestNumber) && requestNumber.Length > 10 && (isIAORestrictedRequestManager || isassigneeorwatcher))
                    return _requestDA.GetAXISRequestString(requestNumber);
                else
                    return "";
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, string.Format($"Exception happened while GET operations of request - {requestNumber}, Error Message : {ex.Message} , Stack Trace :{ex.StackTrace}"));
                return string.Format($"Exception happened while GET operations of request - {requestNumber}, Error Message : {ex.Message}");
            }

        }
    }
}
