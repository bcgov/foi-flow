namespace MCS.FOI.Integration.Application.Queries.GetTemplates
{
    public class GetTemplatesQueryHandler : IQueryHandler<GetTemplatesQuery, IEnumerable<TemplateResult>>
    {
        private readonly ITemplateRepository _templateRepository;

        public GetTemplatesQueryHandler(ITemplateRepository templateRepository)
        {
            _templateRepository = templateRepository;
        }
        public async Task<IEnumerable<TemplateResult>> Handle(GetTemplatesQuery request, CancellationToken cancellationToken)
        {
            var templates = await _templateRepository.GetAsync();
            var result = IMap.Mapper.Map<IEnumerable<TemplateResult>>(templates);

            return result;
        }
    }
}
