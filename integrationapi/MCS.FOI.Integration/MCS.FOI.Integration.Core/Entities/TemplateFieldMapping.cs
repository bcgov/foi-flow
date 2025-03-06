using MCS.FOI.Integration.Core.Entities.Base;

namespace MCS.FOI.Integration.Core.Entities
{
    public class TemplateFieldMapping: Entity
    {
        public string FieldName { get; set; } = default!;
        public string FieldType { get; set; } = default!;
        public string FieldMapping { get; set; } = default!;
        public bool IsActive { get; set; }
        public string? CreatedBy { get; set; }
        public DateTime CreatedAt { get; set; }
        public string? UpdatedBy { get; set; } = default!;
        public DateTime? UpdatedAt { get; set; }
    }
}
