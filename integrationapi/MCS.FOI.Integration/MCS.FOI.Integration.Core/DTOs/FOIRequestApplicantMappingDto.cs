namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestApplicantMappingDto
    {
        public int FOIRequestApplicantMappingId { get; set; }

        public DateTime CreatedAt { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public string? CreatedBy { get; set; }

        public string? UpdatedBy { get; set; }

        public int? RequestorTypeId { get; set; }

        public int? FOIRequestApplicantId { get; set; }

        public int FOIRequestId { get; set; }

        public int FOIRequestVersionId { get; set; }
    }
}
