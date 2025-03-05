namespace MCS.FOI.Integration.Application.Services.S3Connection
{
    public interface IS3ConnectionService
    {
        Task<List<TemplateInfo>> FetchTemplatesAsync(string fileName, string token, string documentPath, CancellationToken cancellationToken);
    }
}
