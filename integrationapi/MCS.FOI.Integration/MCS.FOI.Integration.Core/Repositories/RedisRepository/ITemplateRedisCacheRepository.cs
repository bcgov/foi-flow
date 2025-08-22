using MCS.FOI.Integration.Core.DTOs;

namespace MCS.FOI.Integration.Core.Repositories.RedisRepository
{
    public interface ITemplateRedisCacheRepository
    {
        Task UpdateCacheTemplateAsync(IEnumerable<TemplateDto> templates);
        Task<TemplateDto?> GetTemplateCacheAsync(string fileName);
        Task<TemplateDto?> SetTemplateCacheAsync(TemplateDto template);
    }
}
