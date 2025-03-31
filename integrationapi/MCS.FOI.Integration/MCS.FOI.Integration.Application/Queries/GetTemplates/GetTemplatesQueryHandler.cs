namespace MCS.FOI.Integration.Application.Queries.GetTemplates
{
    public class GetTemplatesQueryHandler : IQueryHandler<GetTemplatesQuery, IEnumerable<TemplateResult>>
    {
       private readonly ITemplateDataService _templateDataService;

        public GetTemplatesQueryHandler(ITemplateDataService templateDataService)
        {
            _templateDataService = templateDataService;
        }
        public async Task<IEnumerable<TemplateResult>> Handle(GetTemplatesQuery request, CancellationToken cancellationToken)
        {
            var templates = await _templateRepository.GetAsync();
            var result = IMap.Mapper.Map<IEnumerable<TemplateResult>>(templates.OrderBy(x => x.TemplateName));

            return result;
        }
    }
}
