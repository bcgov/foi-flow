namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestDto
    {
        public int FOIRequestId { get; set; }
        public int Version { get; set; }
        public string? RequestType { get; set; }
        public DateTime ReceivedDate { get; set; } = DateTime.Now;
        public bool IsActive { get; set; } = true;
        public string? InitialDescription { get; set; }
        public DateTime? InitialRecordSearchFromDate { get; set; }
        public DateTime? InitialRecordSearchToDate { get; set; }

        // Foreign Key References
        public int? ApplicantCategoryId { get; set; }
        public int? DeliveryModeId { get; set; }
        public int? ReceivedModeId { get; set; }
        public int? FOIRawRequestId { get; set; }
    }
}
