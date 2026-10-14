//using Template = MCS.FOI.Integration.Core.Entities.Template;

namespace MCS.FOI.Integration.Application.Commands.UpdateRedisTemplate
{
    public class UpdateTemplateCacheCommandHandler : ICommandHandler<UpdateTemplateCacheCommand, bool>
    {
        private readonly IS3ConnectionService _s3StorageService;
        private readonly ITemplateRedisCacheRepository _templateCacheService;
        private readonly ITemplateDataService _templateDataService;

        public UpdateTemplateCacheCommandHandler(
            IS3ConnectionService s3StorageService,
            ITemplateRedisCacheRepository templateCacheService,
            ITemplateDataService templateDataService)
        {
            _s3StorageService = s3StorageService;
            _templateCacheService = templateCacheService;
            _templateDataService = templateDataService;
        }

        public async Task<bool> Handle(UpdateTemplateCacheCommand command, CancellationToken cancellationToken)
        {
            var templates = (await GetTemplatesAsync()).ToList();

            if (templates.Count == 0)
                throw new InvalidOperationException("No active templates found for refresh.");

            var fetchTasks = templates.Select(async template =>
            {
                var documentFiles = await _s3StorageService.FetchTemplatesAsync(
                    template.FileName,
                    command.Token,
                    template.DocumentPath,
                    cancellationToken);

                var encodedContent = documentFiles?.FirstOrDefault()?.Text;

                if (string.IsNullOrWhiteSpace(encodedContent))
                {
                    throw new InvalidOperationException(
                        $"S3 returned no content for template '{template.FileName}'.");
                }

                template.EncodedContent = encodedContent;
            });

            await Task.WhenAll(fetchTasks);

            await _templateDataService.UpdateTemplates(templates);
            await _templateCacheService.UpdateCacheTemplateAsync(templates);

            return true;
        }

        private async Task<IEnumerable<TemplateDto>> GetTemplatesAsync()
        {
            return await _templateDataService.GetAllTemplates();
        }
    }
}