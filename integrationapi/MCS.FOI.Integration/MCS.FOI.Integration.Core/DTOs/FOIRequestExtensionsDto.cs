namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestExtensionsDto
    {
        public int FOIRequestExtensionId { get; set; }

        public int? ExtendedDueDays { get; set; }

        public DateTime? ExtendedDueDate { get; set; }

        public DateTime? DecisionDate { get; set; }

        public int? ApprovedNoOfDays { get; set; }

        public int? Version { get; set; }

        public bool IsActive { get; set; }

        public DateTime CreatedAt { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public string? CreatedBy { get; set; }

        public string? UpdatedBy { get; set; }

        public int FOIMinistryRequestId { get; set; }

        public int FOIMinistryRequestVersionId { get; set; }

        public int ExtensionStatusId { get; set; }

        public int ExtensionReasonId { get; set; }
    }
}
