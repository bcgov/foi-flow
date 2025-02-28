using MCS.FOI.Integration.Application.Mapper;

namespace MCS.FOI.Integration.API.Controllers
{
    [Route("api/[controller]")]
    [EnableCors(PolicyName = "FOIOrigins")]
    [Authorize(Policy = "IAOTeam")]
    public class TemplateController : BaseController
    {
        public TemplateController(ISender sender) : base(sender) { }

        [HttpPost("GetCorrespondenceByName")]
        public async Task<ActionResult<string>> GetCorrespondenceByName(
            [FromBody] GetCorrespondenceRequest request, CancellationToken cancellationToken)
        {
            if (!Request.TryGetAuthorizationToken(out var token))
            {
                return Unauthorized("Authorization header is missing.");
            }

            var command = IMap.Mapper.Map<GetCorrespondenceCommand>(request);
            command.Token = token;
            var result = await _sender.Send(command, cancellationToken);
            return Ok(result);
        }

        [HttpPost("UpdateTemplateCache")]
        public async Task<ActionResult<bool>> UpdateTemplateCache(CancellationToken cancellationToken)
        {
            if (!Request.TryGetAuthorizationToken(out var token))
            {
                return Unauthorized("Authorization header is missing.");
            }

            UpdateTemplateCacheCommand request = new UpdateTemplateCacheCommand();
            request.Token = token;
            var result = await _sender.Send(request, cancellationToken);
            return Ok(result);
        }

        [HttpGet("GetTemplates")]
        public async Task<ActionResult<IEnumerable<TemplateResult>>> GetTemplates(
           [FromQuery] GetTemplatesQuery request, CancellationToken cancellationToken)
        {
            var result = await _sender.Send(request, cancellationToken);
            return Ok(result);
        }
    }
}
