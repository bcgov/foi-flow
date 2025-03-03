namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestApplicantInfoDto
    {
        public int FOIRequestApplicantMappingId { get; set; }
        public int FOIRequestId { get; set; }
        public int Version { get; set; }
        public int RequestorTypeId { get; set; }
        public string? RequestorType { get; set; }
        public int FOIRequestApplicantId { get; set; }
        public string? FirstName { get; set; }
        public string? MiddleName { get; set; }
        public string? LastName { get; set; }
        public string? AlsoKnownAs { get; set; }
        public DateTime DOB { get; set; }
        public string? BusinessName { get; set; }
        public int? AxisApplicantId { get; set; }
    }
}
