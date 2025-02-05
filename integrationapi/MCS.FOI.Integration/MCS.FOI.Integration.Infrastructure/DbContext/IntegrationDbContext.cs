namespace MCS.FOI.Integration.Infrastructure.Data
{
    public class IntegrationDbContext : DbContext, IIntegrationDbContext
    {
        public IntegrationDbContext(DbContextOptions<IntegrationDbContext> options) : base(options) { }

        public DbSet<Template> Template { get; set; }
        public DbSet<TemplateFieldMapping> TemplateFieldMapping { get; set; }
        public DbSet<TemplateListOptions> TemplateListOptions { get; set; }
    }
}
