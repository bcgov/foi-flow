using Amazon;
using Amazon.S3;
using Amazon.S3.Model;
using FOIMOD.HistoricalDocMigration.Models.FOIFLOWDestination;

namespace FOIMOD.HistoricalDocMigration.Utils
{
    public class DocMigrationS3Client
    {
        private readonly IAmazonS3 _s3Client;

        public DocMigrationS3Client(IAmazonS3 s3Client)
        {
            _s3Client = s3Client;
        }

        private string GetPresignedURL(IAmazonS3 s3, string fileName, HttpVerb method)
        {
            AWSConfigsS3.UseSignatureVersion4 = true;
            GetPreSignedUrlRequest request = new()
            {
                Key = fileName,
                Verb = method,
                Expires = DateTime.Now.AddHours(1),
                Protocol = Protocol.HTTPS,
            };
            return s3.GetPreSignedURL(request);
        }

        public async Task<HttpResponseMessage> UploadFileAsync(UploadFile file)
        {
            var presignedPutURL = this.GetPresignedURL(_s3Client, string.Format("{0}/{1}",file.SubFolderPath,file.DestinationFileName), HttpVerb.PUT);
            using var client = new HttpClient();
            client.Timeout = TimeSpan.FromMinutes(30);
            file.FileStream.Position = 0;
            using (StreamContent strm = new(file.FileStream))
            {
                strm.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");
                return await client.PutAsync(presignedPutURL, strm);
            }

        }
    }
}