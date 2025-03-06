using MCS.FOI.Integration.Core.Repositories.RedisRepository;

namespace MCS.FOI.Integration.Infrastructure.Extensions
{
    public class RedisDataContextSeed
    {
        private const string CachePrefix = "Template_";

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
                await SeedTemplatesBase64FormatAsync(dbContext, redisContext, logger);
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

        private static async Task SeedTemplatesBase64FormatAsync(
            IIntegrationDbContext dbContext,
            IRedisDbContext redisContext,
            ILogger logger)
        {
            if (!redisContext.IsConnected) return;

            var batch = redisContext.Redis.CreateBatch();
            var table = await dbContext.Template
                .AsNoTracking()
                .ToListAsync();

            if (table.Any())
            {
                var tasks = table.Select(template =>
                {
                    var key = $"{CachePrefix}{template.FileName.Trim()}";
                    return batch.StringSetAsync(key, JsonConvert.SerializeObject(template));
                }).ToList();

                batch.Execute();
                await Task.WhenAll(tasks);
                logger.LogInformation("Redis caching completed for all templates.");
            }
            else
            {
                logger.LogWarning("No templates found for caching.");
            }
        }
    }
}
