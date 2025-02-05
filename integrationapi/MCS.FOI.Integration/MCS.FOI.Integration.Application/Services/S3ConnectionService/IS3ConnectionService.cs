namespace MCS.FOI.Integration.Application.Services.S3Connection
{
    public interface IS3ConnectionService
    {
        Task<List<TemplateModel>> FetchTemplatesAsync(GetCorrespondenceCommand message, string documentPath, CancellationToken cancellationToken);
    }
}
