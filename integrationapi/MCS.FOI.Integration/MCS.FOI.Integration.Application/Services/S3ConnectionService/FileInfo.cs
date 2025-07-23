namespace MCS.FOI.Integration.Application.Services.S3Connection
{
    public class FileInfo
    {
        public required string Filename { get; set; }
        public required string S3SourceUri { get; set; }
    }

}
