namespace MCS.FOI.Integration.Core.DTOs
{
    public class PaymentDto
    {
        public int PaymentId { get; set; }

        public int FeeCodeId { get; set; }

        public int Quantity { get; set; }

        public float Total { get; set; }

        public string? Status { get; set; } 

        public int RequestId { get; set; }
        public DateTime CreatedOn { get; set; }

        public DateTime? CompletedOn { get; set; }

        public string? PaybcUrl { get; set; }

        public string? ResponseUrl { get; set; }

        public string? OrderId { get; set; }

        public string? TransactionNumber { get; set; }
    }
}
