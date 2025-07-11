namespace MCS.FOI.Integration.Application.Queries.GetTemplates
{
    public class GetTemplatesQuery: IQuery<IEnumerable<TemplateResult>>{}

    public class TemplateResult
    {
        public string FileName { get; set; } = default!;
        public string TemplateName { get; set; } = default!;
        public string Extension { get; set; } = default!;
        public bool IsActive { get; set; }
        public string RequestType { get; set; } = default!;
        public string TemplateType { get; set; } = default!;
        public string DocumentPath { get; set; } = default!;
        public string EncodedContent { get; set; } = default!;
        public string? CreatedBy { get; set; }
        public DateTime CreatedAt { get; set; }
        public string? UpdatedBy { get; set; } = default!;
        public DateTime? UpdatedAt { get; set; }
    }
}
