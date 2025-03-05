namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestApplicationFeeDto
    {
        public int ApplicationFeeId { get; set; }
        public int Version { get; set; }
        public int RawRequestId { get; set; }
        public string? ApplicationFeeStatus { get; set; }
        public double? AmountPaid { get; set; }
        public string? PaymentSource { get; set; }
        public DateTime? PaymentDate { get; set; }
        public string? OrderId { get; set; }
        public string? TransactionNumber { get; set; }
        public double? RefundAmount { get; set; }
        public DateTime? RefundDate { get; set; }
        public string? ReasonForRefund { get; set; }
    }
}
