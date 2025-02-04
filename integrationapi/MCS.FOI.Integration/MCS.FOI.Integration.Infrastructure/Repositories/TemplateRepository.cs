namespace MCS.FOI.Integration.Core.Repositories
{
    public class TemplateRepository : EFRepository<Template>, ITemplateRepository
    {
        private readonly IntegrationDbContext _context;
        public TemplateRepository(IntegrationDbContext context) : base(context) 
        { 
            _context = context;
        }
    }
}
