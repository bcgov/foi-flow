namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestCFRFeesDto
    {
        public int CFRFeeId { get; set; }

        public int MinistryRequestId { get; set; }

        public int MinistryRequestVersion { get; set; }

        public int Version { get; set; }

        public string? FeeData { get; set; }

        public string? OverallSuggestions { get; set; }

        public int CFRFeeStatusId { get; set; }

        public DateTime CreatedAt { get; set; }

        public string? CreatedBy { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public string? UpdatedBy { get; set; }

        public int? CFRFormReasonId { get; set; }

    }
}
