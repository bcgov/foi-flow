namespace MCS.FOI.Integration.Infrastructure.Extensions
{
    public static class DatabaseExtension
    {
        public static async Task ConfigureMigrationAsync(this WebApplication app, WebApplicationBuilder builder)
        {
            await app.MigrateDatabaseAsync<IntegrationDbContext>(async (context, services) =>
            {
                var configMigrationsTimeout = builder.Configuration.GetValue<int>("MigrationsTimeout");
                await IntegrationContextSeed.SeedDatabaseAsync(context, configMigrationsTimeout);

                var logger = services.GetService<ILogger<RedisDataContextSeed>>();
                var redisContext = services.GetRequiredService<IRedisDbContext>();
                await RedisDataContextSeed.SeedRedisAsync(context, redisContext, logger);
            });
        }

        private static async Task<IHost> MigrateDatabaseAsync<TContext>(this IHost host, Func<TContext, IServiceProvider, Task> seeder)
            where TContext : DbContext
        {
            using (var scope = host.Services.CreateScope())
            {
                var services = scope.ServiceProvider;
                var logger = services.GetRequiredService<ILogger<TContext>>();
                var context = services.GetService<TContext>();

                if (context == null)
                {
                    logger.LogError("DbContext {Context} is not available.", typeof(TContext).Name);
                    throw new InvalidOperationException($"DbContext {typeof(TContext).Name} not found.");
                }

                try
                {
                    logger.LogInformation("Starting database migration: {Context}", typeof(TContext).Name);

                    var retry = Policy.Handle<Exception>()
                        .WaitAndRetryAsync(
                            retryCount: 5,
                            sleepDurationProvider: retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                            onRetry: (exception, span, retryAttempt, context) =>
                            {
                                logger.LogWarning(exception, "Retry {RetryAttempt} for database migration: {Context}", retryAttempt, typeof(TContext).Name);
                            });

                    await retry.ExecuteAsync(() => CallSeederAsync(seeder, context, services));

                    logger.LogInformation("Database migration completed: {Context}", typeof(TContext).Name);
                }
                catch (Exception ex)
                {
                    logger.LogError(ex, "An error occurred while migrating the database {Context}", typeof(TContext).Name);
                    throw;
                }
            }

            return host;
        }

        private static async Task CallSeederAsync<TContext>(Func<TContext, IServiceProvider, Task> seeder, TContext context, IServiceProvider services)
            where TContext : DbContext
        {
            try
            {
                if (context.Database.GetPendingMigrations().Any())
                {
                    await context.Database.MigrateAsync();
                }

                await seeder(context, services);
            }
            catch (Exception ex)
            {
                var logger = services.GetRequiredService<ILogger<TContext>>();
                logger.LogError(ex, "An error occurred during seeding for {Context}", typeof(TContext).Name);
                throw;
            }
        }
    }
}
