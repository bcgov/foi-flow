namespace MCS.FOI.Integration.Core.Repositories
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
