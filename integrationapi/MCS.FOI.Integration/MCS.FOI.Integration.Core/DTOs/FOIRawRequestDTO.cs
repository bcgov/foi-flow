using System.Text.Json;

namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRawRequestDTO
    {
        public int RequestId { get; set; }
        public int Version { get; set; }
        public string RequestRawData { get; set; }
        public string Status { get; set; }
        public string RequestStatusLabel { get; set; }
        public string Notes { get; set; }
        public Guid? WfInstanceId { get; set; }
        public string AssignedGroup { get; set; }
        public string AssignedTo { get; set; }
        public DateTime Created_At { get; set; }
        public DateTime? Updated_At { get; set; }
        public string CreatedBy { get; set; }
        public string UpdatedBy { get; set; }
        public string SourceOfSubmission { get; set; }
        public bool IsPiiRedacted { get; set; }
        public DateTime? CloseDate { get; set; }
        public bool? RequiresPayment { get; set; }
        public DateTime? AxisSyncDate { get; set; }
        public string AxisRequestId { get; set; }
        public string LinkedRequests { get; set; }
        public bool IsIaoRestricted { get; set; }
        public int? CloseReasonId { get; set; }
    }
}
