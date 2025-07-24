namespace MCS.FOI.Integration.Core.DTOs
{
    public class OperatingTeamEmailsDto
    {
        public int EmailId { get; set; }

        public string? EmailAddress { get; set; }

        public bool IsActive { get; set; }

        public DateTime CreatedAt { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public int TeamId { get; set; }
    }
}
