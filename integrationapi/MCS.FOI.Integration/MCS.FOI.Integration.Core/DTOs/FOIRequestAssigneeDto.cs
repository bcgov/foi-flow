namespace MCS.FOI.Integration.Core.DTOs
{
    public class FOIRequestAssigneeDto
    {
        public int Version { get; set; }
        public string AssignedTo { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public string BCGovCode { get; set; }
        public int ProgramAreaId { get; set; }
        public string RequestType { get; set; }
        public bool IsOIPCReview { get; set; }

    }
}
