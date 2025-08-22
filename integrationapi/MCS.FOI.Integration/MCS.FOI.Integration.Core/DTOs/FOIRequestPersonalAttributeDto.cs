namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestPersonalAttributeDto
    {
        public int FOIRequestPersonalAttributeId { get; set; }

        public string AttributeValue { get; set; }

        public DateTime CreatedAt { get; set; } = DateTime.Now;

        public DateTime? UpdatedAt { get; set; }

        public string CreatedBy { get; set; }

        public string UpdatedBy { get; set; }

        public int PersonalAttributeId { get; set; }

        public int FOIRequestId { get; set; }

        public int FOIRequestVersionId { get; set; }
        public string AttributeName { get; set; }
    }
}
