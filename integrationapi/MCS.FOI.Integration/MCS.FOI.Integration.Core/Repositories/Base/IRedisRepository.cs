namespace MCS.FOI.Integration.Core.Repositories.Base
{
    public interface IRedisRepository<T>
    {
        Task<T?> GetCacheValueAsync(string key);
        Task<T?> SetCacheValueAsync(string key, T data, TimeSpan? expiry = null);
        Task<bool> DeleteCacheValueAsync(string key);
    }
}
