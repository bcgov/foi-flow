namespace MCS.FOI.Integration.Infrastructure.Data
{
    public class IntegrationDbContext : DbContext, IIntegrationDbContext
    {
        public IntegrationDbContext(DbContextOptions<IntegrationDbContext> options) : base(options) { }
    }
}
