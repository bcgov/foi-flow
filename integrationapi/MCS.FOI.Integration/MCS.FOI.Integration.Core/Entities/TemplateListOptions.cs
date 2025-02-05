using MCS.FOI.Integration.Core.Entities.Base;

namespace MCS.FOI.Integration.Core.Entities
{
    public class TemplateListOptions: Entity
    {
        public string Code { get; set; } = default!;
        public string Description { get; set; } = default!;
        public string? CreatedBy { get; set; }
        public DateTime CreatedAt { get; set; }
        public string? UpdatedBy { get; set; } = default!;
        public DateTime? UpdatedAt { get; set; }
    }
}
