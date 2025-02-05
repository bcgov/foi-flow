namespace MCS.FOI.Integration.Infrastructure.Data
{
    public interface IIntegrationDbContext
    {
        public DbSet<Template> Template { get; set; }
        public DbSet<TemplateFieldMapping> TemplateFieldMapping { get; set; }
        public DbSet<TemplateListOptions> TemplateListOptions { get; set; }
    }
}
