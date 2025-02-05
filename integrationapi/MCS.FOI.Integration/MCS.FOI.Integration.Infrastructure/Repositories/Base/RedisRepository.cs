namespace MCS.FOI.Integration.Infrastructure.Repositories.Base
{
    public class RedisRepository<T> : IRedisRepository<T>
    {
        private readonly IRedisDbContext _context;

        public RedisRepository(IRedisDbContext context) => _context = context;

        public async Task<T?> GetCacheValueAsync(string key)
        {
            if (string.IsNullOrWhiteSpace(key))
                throw new ArgumentException("Key cannot be null or whitespace", nameof(key));

            if (!_context.IsConnected) return default;

            try
            {
                var data = await _context.Redis.StringGetAsync(key).ConfigureAwait(false);
                return data.IsNullOrEmpty ? default : JsonConvert.DeserializeObject<T>(data);
            }
            catch (Exception ex)
            {
                throw new ApplicationException($"Error retrieving cache value for key: {key}", ex);
            }
        }

        public async Task<T?> SetCacheValueAsync(string key, T data, TimeSpan? expiry = null)
        {
            if (string.IsNullOrWhiteSpace(key))
                throw new ArgumentException("Key cannot be null or whitespace", nameof(key));

            if (data == null)
                throw new ArgumentNullException(nameof(data));

            if (!_context.IsConnected) return default;

            try
            {
                await _context.Redis.StringSetAsync(key, JsonConvert.SerializeObject(data), expiry).ConfigureAwait(false);
                return await GetCacheValueAsync(key).ConfigureAwait(false);
            }
            catch (Exception ex)
            {
                throw new ApplicationException($"Error setting cache value for key: {key}", ex);
            }
        }

        public async Task<bool> DeleteCacheValueAsync(string key)
        {
            if (string.IsNullOrWhiteSpace(key))
                throw new ArgumentException("Key cannot be null or whitespace", nameof(key));

            if (!_context.IsConnected) return false;

            try
            {
                return await _context.Redis.KeyDeleteAsync(key).ConfigureAwait(false);
            }
            catch (Exception ex)
            {
                throw new ApplicationException($"Error deleting cache value for key: {key}", ex);
            }
        }
    }
}
