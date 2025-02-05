namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestContactInformationDto
    {
        public int FOIRequestContactId { get; set; }

        public string? ContactInformation { get; set; }

        public string? DataFormat { get; set; }

        public DateTime CreatedAt { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public string? CreatedBy { get; set; }

        public string? UpdatedBy { get; set; }

        public int? ContactTypeId { get; set; }

        public int FOIRequestId { get; set; }

        public int FOIRequestVersionId { get; set; }
    }
}
