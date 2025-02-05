namespace MCS.FOI.Integration.Application.Queries.GetListOptions
{
    public class GetListOptionsQueryHandler : IQueryHandler<GetListOptionsQuery, IEnumerable<ListOptionsResult>>
    {
        private readonly ITemplateListOptionRepository _templateListOptionRepository;
        public GetListOptionsQueryHandler(ITemplateListOptionRepository templateListOptionRepository)
        {
            _templateListOptionRepository = templateListOptionRepository;
        }

        public async Task<IEnumerable<ListOptionsResult>> Handle(GetListOptionsQuery request, CancellationToken cancellationToken)
        {
            var templates = await _templateListOptionRepository.GetAsync();
            var result = IMap.Mapper.Map<IEnumerable<ListOptionsResult>>(templates);

            return result;
        }
    }
}
