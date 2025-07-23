namespace MCS.FOI.Integration.API.Controllers
{
    [ApiController]
    public class BaseController: ControllerBase
    {
        protected readonly ISender _sender;

        public BaseController(ISender sender) => _sender = sender;
    }
}
