namespace MCS.FOI.Integration.Application.Services.S3Connection
{
    public interface IS3ConnectionService
    {
        Task<List<TemplateInfo>> FetchTemplatesAsync(GetCorrespondenceCommand message, string documentPath, CancellationToken cancellationToken);
    }
}
