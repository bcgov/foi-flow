namespace MCS.FOI.Integration.Infrastructure.Repositories
{
    public class TemplateRepository : EFRepository<Template>, ITemplateRepository
    {
        private readonly IntegrationDbContext _context;
        private readonly IRedisDbContext _redisDbContext;

        public TemplateRepository(
            IntegrationDbContext context, 
            IRedisDbContext redisDbContext) : base(context)
        {
            _context = context;
            _redisDbContext = redisDbContext;
        }
    }
}
