using MCS.FOI.Integration.Core.DTOs;
using MCS.FOI.Integration.Core.Repositories.RedisRepository;

namespace MCS.FOI.Integration.Infrastructure.Repositories.RedisRepository
{
    public class TemplateRedisCacheRepository : ITemplateRedisCacheRepository
    {
        private readonly IRedisDbContext _redisDbContext;
        private readonly IRedisRepository<TemplateDto> _redisRepository;
        private const string CachePrefix = "Template_";

        public TemplateRedisCacheRepository(
            IRedisDbContext redisDbContext,
            IRedisRepository<TemplateDto> redisRepository)
        {
            _redisDbContext = redisDbContext;
            _redisRepository = redisRepository;
        }

        public async Task UpdateCacheTemplateAsync(IEnumerable<TemplateDto>? templates)
        {
            if (!_redisDbContext.IsConnected || !templates.Any()) return;

            var batch = _redisDbContext.Redis.CreateBatch();
            var tasks = templates.Select(template =>
            {
                var key = $"{CachePrefix}{template.FileName.Trim()}";
                return batch.StringSetAsync(key, JsonConvert.SerializeObject(template));
            }).ToList();

            batch.Execute();
            await Task.WhenAll(tasks);
        }

        public async Task<TemplateDto?> GetTemplateCacheAsync(string fileName)
        {
            if (!_redisDbContext.IsConnected) return null;

            var key = $"{CachePrefix}{fileName.Trim()}";
            return await _redisRepository.GetCacheValueAsync(key);
        }

        public async Task<TemplateDto?> SetTemplateCacheAsync(TemplateDto template)
        {
            if (!_redisDbContext.IsConnected) return null;

            var key = $"{CachePrefix}{template.FileName.Trim()}";
            return await _redisRepository.SetCacheValueAsync(key, template);
        }
    }
}
