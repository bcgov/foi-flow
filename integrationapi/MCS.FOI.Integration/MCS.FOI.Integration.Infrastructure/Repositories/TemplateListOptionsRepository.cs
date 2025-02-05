namespace MCS.FOI.Integration.Core.Repositories
{
    public class TemplateListOptionRepository: EFRepository<TemplateListOptions>, ITemplateListOptionRepository
    {
        private readonly IntegrationDbContext _context;
        public TemplateListOptionRepository(IntegrationDbContext context) : base(context)
        {
            _context = context;  
        }
    }
}
