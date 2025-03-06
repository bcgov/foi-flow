namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIMinistryRequestDto
    {
        public int FOIMinistryRequestId { get; set; }

        public int Version { get; set; }

        public bool IsActive { get; set; }

        public string? FileNumber { get; set; }

        public string? Description { get; set; }

        public DateTime? RecordSearchFromDate { get; set; }

        public DateTime? RecordSearchToDate { get; set; }

        public DateTime StartDate { get; set; }

        public DateTime DueDate { get; set; }

        public DateTime? CFRDueDate { get; set; }

        public DateTime? OriginalLDD { get; set; }

        public string? AssignedGroup { get; set; }

        public string? AssignedTo { get; set; }

        public DateTime CreatedAt { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public string? CreatedBy { get; set; }

        public string? UpdatedBy { get; set; }

        public string? AssignedMinistryPerson { get; set; }

        public string? AssignedMinistryGroup { get; set; }

        public DateTime? CloseDate { get; set; }

        public DateTime? AxisSyncDate { get; set; }

        public string? AxisRequestId { get; set; }

        public string? AxisPageCount { get; set; }

        public string? AxisLanPageCount { get; set; }

        public string? RecordsPageCount { get; set; }

        public int? EstimatedPageCount { get; set; }

        public int? EstimatedTaggedPageCount { get; set; }

        public string? LinkedRequests { get; set; }

        public string? IdentityVerified { get; set; }

        public string? MinistrySignOffApproval { get; set; }

        public string? RequestStatusLabel { get; set; }

        public bool? UserRecordsLockStatus { get; set; }

        public int? CloseReasonId { get; set; }

        public int? ProgramAreaId { get; set; }

        public int? RequestStatusId { get; set; }

        public int FOIRequestId { get; set; }

        public int FOIRequestVersionId { get; set; }

        public bool? IsOfflinePayment { get; set; }

        public bool? IsOIPCReview { get; set; }

    }
}
