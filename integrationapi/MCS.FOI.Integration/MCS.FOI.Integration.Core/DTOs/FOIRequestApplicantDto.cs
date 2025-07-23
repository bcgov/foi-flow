namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestApplicantDto
    {
        public int FOIRequestApplicantId { get; set; }

        public string? FirstName { get; set; }

        public string? MiddleName { get; set; }

        public string? LastName { get; set; }

        public string? AlsoKnownAs { get; set; }

        public DateTime? DOB { get; set; }

        public string? BusinessName { get; set; }

        public DateTime CreatedAt { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public string? CreatedBy { get; set; }

        public string? UpdatedBy { get; set; }

        public string? ApplicantProfileId { get; set; }

        public int? AxisApplicantId { get; set; }
    }
}
