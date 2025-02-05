namespace MCS.FOI.Integration.Infrastructure.Extensions
{
    public class RedisDataContextSeed
    {
        public static async Task SeedRedisAsync(
            IIntegrationDbContext dbContext,
            IRedisDbContext redisContext,
            ILogger<RedisDataContextSeed> logger,
            int? retry = 0)
        {
            if (dbContext == null) throw new ArgumentNullException(nameof(dbContext));
            if (redisContext == null) throw new ArgumentNullException(nameof(redisContext));

            int retryCount = retry ?? 0;

            try
            {
                logger.LogInformation("Starting Redis seeding...");
                await SeedListValuesAsync(dbContext, redisContext, logger);
                logger.LogInformation("Redis seeding completed successfully.");
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "An error occurred during Redis seeding.");

                if (retryCount < 3)
                {
                    retryCount++;
                    logger.LogWarning($"Retrying Redis seeding... Attempt {retryCount}/3");
                    await SeedRedisAsync(dbContext, redisContext, logger, retryCount);
                }
                else
                {
                    logger.LogCritical("Redis seeding failed after 3 retries.");
                    throw;
                }
            }
        }

        private static async Task SeedListValuesAsync(
            IIntegrationDbContext dbContext,
            IRedisDbContext redisContext,
            ILogger logger)
        {
            var batch = redisContext.Redis.CreateBatch();
            var tasks = new List<Task>();

            var table = await dbContext.Template
                .AsNoTracking()
                .ToListAsync();

            if (table.Any())
            {
                

                batch.Execute();
                await Task.WhenAll(tasks);
                logger.LogInformation("Redis caching completed for all list values.");
            }
            else
            {
                logger.LogWarning("No list values found for caching.");
            }
        }
    }
}
