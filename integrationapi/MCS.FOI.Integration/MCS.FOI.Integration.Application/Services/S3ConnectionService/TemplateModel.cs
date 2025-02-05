namespace MCS.FOI.Integration.Application.Services.S3Connection
{
    public class TemplateModel
    {
        public required string Value { get; set; }
        public required string TemplateId { get; set; }
        public required string Text { get; set; }
        public bool Disabled { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}
