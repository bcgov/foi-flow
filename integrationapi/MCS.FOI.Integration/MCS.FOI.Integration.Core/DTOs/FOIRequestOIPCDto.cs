namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestOIPCDto
    {
        public int OipcId { get; set; }
        public int? FOIMinistryRequestId { get; set; }
        public int? FOIMinistryRequestVersionId { get; set; }
        public string? OipcNo { get; set; }

        // Relationships
        public int? ReviewTypeId { get; set; }
        public OIPCReviewType? ReviewType { get; set; }

        public int? ReasonId { get; set; }
        public OIPCReason? Reason { get; set; }

        public int? StatusId { get; set; }
        public OIPCStatus? Status { get; set; }

        public int? OutcomeId { get; set; }
        public OIPCOutcome? Outcome { get; set; }

        // Additional Attributes
        public bool? IsInquiry { get; set; }
        public Dictionary<string, object>? InquiryAttributes { get; set; }
        public bool? IsJudicialReview { get; set; }
        public bool? IsSubsequentAppeal { get; set; }
        public string? Investigator { get; set; }
        public DateTime? ReceivedDate { get; set; }
        public DateTime? ClosedDate { get; set; }

        // Audit Fields
        public DateTime CreatedAt { get; set; } = DateTime.Now;
        public string CreatedBy { get; set; } = string.Empty;
        public DateTime? UpdatedAt { get; set; }
        public string? UpdatedBy { get; set; }
    }

    // Related DTOs
    public class OIPCReviewType
    {
        public int ReviewTypeId { get; set; }
        public string? Name { get; set; }
    }

    public class OIPCReason
    {
        public int ReasonId { get; set; }
        public string? Description { get; set; }
    }

    public class OIPCStatus
    {
        public int StatusId { get; set; }
        public string? StatusName { get; set; }
    }

    public class OIPCOutcome
    {
        public int OutcomeId { get; set; }
        public string? OutcomeName { get; set; }
    }
}
