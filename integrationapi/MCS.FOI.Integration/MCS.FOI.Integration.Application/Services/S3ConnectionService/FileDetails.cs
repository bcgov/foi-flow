namespace MCS.FOI.Integration.Application.Services.S3Connection
{
    public class FileDetails
    {
        public required string Filename { get; set; }
        public required string S3SourceUri { get; set; }
        public required string Filepath { get; set; }
        public required string Authheader { get; set; }
        public required string Amzdate { get; set; }
        public required string Uniquefilename { get; set; }
        public required string Filestatustransition { get; set; }
    }
}
