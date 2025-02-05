namespace MCS.FOI.Integration.Core.DTOs
{
    public class TemplateFieldDto
    {
        public int Id { get; set; }
        public string TemplateId { get; set; } = default!;
        public string FieldName { get; set; } = default!;
    }
}
