namespace MCS.FOI.Integration.Application.Services.S3Connection
{
    public class S3ConnectionService : IS3ConnectionService
    {
        private static readonly HttpClient _httpClient = new HttpClient();
        private readonly ILogger<S3ConnectionService> _logger;
        private readonly IConfiguration _configuration;
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly string _correspondenceUrl;

        public S3ConnectionService(
            ILogger<S3ConnectionService> logger,
            IConfiguration configuration,
            IHttpClientFactory httpClientFactory)
        {
            _logger = logger;
            _configuration = configuration;
            _httpClientFactory = httpClientFactory;
            _correspondenceUrl = _configuration.GetValue<string>("ApiSettings:CorrespondenceUrl") ?? string.Empty;
        }

        public async Task<List<TemplateModel>> FetchTemplatesAsync(GetCorrespondenceCommand message, string documentPath, CancellationToken cancellationToken)
        {
            var s3host = _configuration.GetValue<string>("AWSS3:OSS_S3_HOST") ?? string.Empty;
            var bucket = _configuration.GetValue<string>("AWSS3:OSS_S3_FORMS_BUCKET") ?? string.Empty;

            var fileInfoList = new List<object>
            {
                new
                {
                    filename = message.FileName,
                    s3sourceuri = $"{s3host}/{bucket}{documentPath}"
                }
            };

            var response = await HttpPostRequest(_correspondenceUrl, fileInfoList, message.Token, cancellationToken);
            var resultJson = await response.Content.ReadAsStringAsync(cancellationToken);
            var s3fileResponse = JsonConvert.DeserializeObject<List<FileDetails>>(resultJson) ?? new List<FileDetails>();

            var fileBytes = await GetOSSHeaderDetailsAsync(message, s3fileResponse);

            var templates = new List<TemplateModel>();
            if (fileBytes.Length > 0)
            {
                var templateItem = new TemplateModel
                {
                    Value = message.FileName,
                    TemplateId = Guid.NewGuid().ToString(),
                    Text = Convert.ToBase64String(fileBytes),
                    Disabled = false,
                    CreatedAt = DateTime.UtcNow
                };

                templates.Add(templateItem);
            }

            return templates;
        }

        public async Task<byte[]> GetOSSHeaderDetailsAsync(GetCorrespondenceCommand message, List<FileDetails> s3fileResponse)
        {
            if (!s3fileResponse.Any())
            {
                _logger.LogError("S3 file response is empty.");
                return Array.Empty<byte>();
            }

            var s3FileDetails = s3fileResponse.First();
            var url = s3FileDetails.S3SourceUri;

            try
            {
                var request = new HttpRequestMessage(HttpMethod.Get, url);
                AddHeaderIfPresent(request, "X-Amz-Date", s3FileDetails.Amzdate);
                AddHeaderIfPresent(request, "Authorization", s3FileDetails.Authheader);

                var response = await _httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);
                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError($"Failed to download document. Status: {response.StatusCode}");
                    return Array.Empty<byte>();
                }

                await using var memoryStream = new MemoryStream();
                await response.Content.CopyToAsync(memoryStream);
                return memoryStream.ToArray();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Exception occurred in GetOSSHeaderDetailsAsync");
                return Array.Empty<byte>();
            }
        }

        private static void AddHeaderIfPresent(HttpRequestMessage request, string headerName, string? headerValue)
        {
            if (!string.IsNullOrWhiteSpace(headerValue))
            {
                request.Headers.TryAddWithoutValidation(headerName, headerValue);
            }
        }

        public async Task<HttpResponseMessage> HttpPostRequest(string url, object data, string token, CancellationToken cancellationToken)
        {
            var client = _httpClientFactory.CreateClient();
            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var request = new HttpRequestMessage(HttpMethod.Post, url)
            {
                Content = content
            };

            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

            var response = await client.SendAsync(request, cancellationToken);
            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError($"Error in HTTP POST request to {url}: {response.StatusCode}");
            }

            return response;
        }
    }
}
