using Template = MCS.FOI.Integration.Core.Entities.Template;

namespace MCS.FOI.Integration.Application.Commands.UpdateRedisTemplate
{
    public class UpdateTemplateCacheCommandHandler : ICommandHandler<UpdateTemplateCacheCommand, bool>
    {
        private readonly IS3ConnectionService _s3StorageService;
        private readonly ITemplateRepository _templateRepository;
        private readonly ITemplateRedisCacheRepository _templateCacheService;

        public UpdateTemplateCacheCommandHandler(
            IS3ConnectionService s3StorageService,
            ITemplateRepository templateRepository,
            ITemplateRedisCacheRepository templateCacheService)
        {
            _s3StorageService = s3StorageService;
            _templateRepository = templateRepository;
            _templateCacheService = templateCacheService;
        }

        public async Task<bool> Handle(UpdateTemplateCacheCommand command, CancellationToken cancellationToken)
        {
            try
            {
                var templates = await GetTemplatesAsync();

                var fetchTasks = templates.Select(async template =>
                {
                    var documentFiles = await _s3StorageService.FetchTemplatesAsync(
                        template.FileName, command.Token, template.DocumentPath, cancellationToken);
                    template.EncodedContent = documentFiles?.FirstOrDefault()?.Text ?? string.Empty;
                });

                await Task.WhenAll(fetchTasks);

                var updatedTemplates = IMap.Mapper.Map<IEnumerable<Template>>(templates);
                await _templateRepository.BulkInsertOrUpdateAsync(updatedTemplates);
                await _templateRepository.SaveChangesAsync();
                await _templateCacheService.UpdateCacheTemplateAsync(templates);
            }
            catch (Exception ex)
            {
                new InternalServerException($"Error saving changes: {ex.Message}");
            }

            return true;
        }

        private async Task<IEnumerable<TemplateDto>> GetTemplatesAsync()
        {
            var template = await _templateRepository.GetAllAsync();
            return IMap.Mapper.Map<IEnumerable<TemplateDto>>(template.Where(r => r.IsActive));
        }
    }
}