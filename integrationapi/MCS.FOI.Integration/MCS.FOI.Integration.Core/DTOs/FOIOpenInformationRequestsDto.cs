namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIOpenInformationRequestsDto
    {
        public int FoiOpenInfoRequestId { get; set; }
        public int Version { get; set; }
        public int FoiMinistryRequestId { get; set; }
        public int FoiMinistryRequestVersionId { get; set; }
        public int OiPublicationStatusId { get; set; }
        public int? OiExemptionId { get; set; }
        public string? OiAssignedTo { get; set; }

        public bool? OiExemptionApproved { get; set; }
        public string? PageReference { get; set; }
        public string? IaOrationale { get; set; }
        public string? OiFeedback { get; set; }
        public DateTime? PublicationDate { get; set; }
        public DateTime? OiExemptionDate { get; set; }
        public bool IsActive { get; set; }
        public bool? CopyrightSevered { get; set; }

        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public string? CreatedBy { get; set; }
        public string? UpdatedBy { get; set; }
        public string? ProcessingStatus { get; set; }
        public string? ProcessingMessage { get; set; }
        public string? SitemapPages { get; set; }
        public string? PublicationStatus { get; set; }
        public string? ExemptionName { get; set; }
    }
}
