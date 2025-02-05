namespace MCS.FOI.Integration.Infrastructure.Extensions
{
    public class IntegrationContextSeed
    {
        public static async Task SeedDatabaseAsync(IntegrationDbContext integrationDbContext, int migrationsTimeout)
        {
            if (integrationDbContext == null) throw new ArgumentNullException(nameof(integrationDbContext));

            integrationDbContext.Database.SetCommandTimeout(migrationsTimeout);
            await integrationDbContext.Database.MigrateAsync();

            await SeedDataAsync(integrationDbContext);
        }

        private static async Task SeedDataAsync(IntegrationDbContext integrationDbContext)
        {
            // Placeholder for additional seed logic
            await Task.CompletedTask;
        }
    }
}
