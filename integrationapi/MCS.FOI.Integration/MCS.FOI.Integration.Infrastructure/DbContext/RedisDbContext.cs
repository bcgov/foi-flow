namespace MCS.FOI.Integration.Infrastructure.Data
{
    public class RedisDbContext : IRedisDbContext
    {
        public IDatabase Redis { get; }
        public bool IsConnected { get; }

        public RedisDbContext(ConnectionMultiplexer redisConnection)
        {
            if (redisConnection != null && redisConnection.IsConnected)
            {
                Redis = redisConnection.GetDatabase();
                IsConnected = true;
            }
            else
            {
                Console.WriteLine("Redis is unavailable. RedisContext is running in disconnected mode.");
                Redis = null; // No Redis database available
                IsConnected = false;
            }
        }
    }
}
