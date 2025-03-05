namespace MCS.FOI.Integration.Infrastructure.Repositories
{
    public class TemplateFieldMappingRepository : EFRepository<TemplateFieldMapping>, ITemplateFieldMappingRepository
    {
        private readonly IntegrationDbContext _context;
        public TemplateFieldMappingRepository(IntegrationDbContext context) : base(context)
        {
            _context = context;   
        }
    }
}
