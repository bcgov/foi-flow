namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestPaymentDto
    {
        public int PaymentId { get; set; }

        public int Version { get; set; }

        public int FOIRequestId { get; set; }

        public int? MinistryRequestId { get; set; }

        public int? MinistryRequestVersion { get; set; }

        public string? PaymentUrl { get; set; }

        public DateTime? PaymentExpiryDate { get; set; }

        public decimal? PaidAmount { get; set; }

        public DateTime CreatedAt { get; set; }

        public string? CreatedBy { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public string? UpdatedBy { get; set; }
    }
}
