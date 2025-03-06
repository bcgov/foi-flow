namespace MCS.FOI.Integration.Application.Extensions
{
    public static class HttpRequestExtensions
    {
        public static bool TryGetAuthorizationToken(this HttpRequest request, out string token)
        {
            if (request.Headers.TryGetValue("Authorization", out var authHeader))
            {
                token = authHeader.ToString().Replace("Bearer ", "").Trim();
                return true;
            }

            token = string.Empty;
            return false;
        }
    }
}
