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

        public static string ConvertRequestToJSON(AXISRequest request)
        {
            return JsonConvert.SerializeObject(request);
        }

        private string GetAXISRequestString(AXISRequest axisrequest)
        {
            if (axisrequest.AXISRequestID != null)
                return RequestsHelper.ConvertRequestToJSON(axisrequest);
            return "{}";
        }

        [HttpGet]

        public ActionResult<string> Get(string requestNumber, string type, int id)
        {
            try
            {
                var isIAORestrictedRequestManager = User.HasClaim(claim => claim.Value == "/IAO Restricted Files Manager" && claim.Type == "groups");
                var isassigneeorwatcher = false;


                if (!isIAORestrictedRequestManager)
                {
                    var users = _fOIFlowRequestUser.GetAssigneesandWatchers(id, type);
                    if (users != null)
                    {
                        foreach (var user in users)
                        {
                            isassigneeorwatcher = User.HasClaim(claim => claim.Value.ToUpper() == user.username.ToUpper().Replace("@IDIR", "") && claim.Type == "foi_preferred_username");
                            if (isassigneeorwatcher)
                            {
                                break;
                            }
                        }
                    }
                }


                if (!string.IsNullOrEmpty(requestNumber) && requestNumber.Length > 10 && !string.IsNullOrEmpty(type))
                {
                    AXISRequest axisrequest = _requestDA.GetAXISRequest(requestNumber);
                    var isrestricted = axisrequest.IsRestricted;

                    if (isIAORestrictedRequestManager || !isrestricted)
                        return this.GetAXISRequestString(axisrequest);

                    if (axisrequest != null && axisrequest.AXISRequestID != null)
                    {
                        if (isassigneeorwatcher && isrestricted)
                        {
                            return this.GetAXISRequestString(axisrequest);
                        }
                        else
                        {
                            return  Unauthorized($"Request {axisrequest.AXISRequestID} is a restricted request, Please check your access with Administrator");
                        }

                    }
                    else
                        return "";
                }

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
