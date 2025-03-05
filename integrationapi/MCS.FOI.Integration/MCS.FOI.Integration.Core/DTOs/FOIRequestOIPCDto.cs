namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestOIPCDto
    {
        public int OipcId { get; set; }
        public int? FOIMinistryRequestId { get; set; }
        public int? FOIMinistryRequestVersionId { get; set; }
        public string? OipcNo { get; set; }

        // Additional Attributes
        public bool? IsInquiry { get; set; }
        public string? InquiryAttributes { get; set; }
        public bool? IsJudicialReview { get; set; }
        public bool? IsSubsequentAppeal { get; set; }
        public string? Investigator { get; set; }
        public DateTime? ReceivedDate { get; set; }
        public DateTime? ClosedDate { get; set; }
        public string? Reason { get; set; }

    }
}
