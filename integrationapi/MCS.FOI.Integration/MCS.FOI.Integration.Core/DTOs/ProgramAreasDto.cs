namespace MCS.FOI.Integration.Core.DTOs
{
    public class ProgramAreaDto
    {
        public int ProgramAreaId { get; set; }

        public string? Name { get; set; }

        public string? IAOCCode { get; set; }

        public string? BCGovCode { get; set; }

        public string? Type { get; set; }

        public bool IsActive { get; set; }
    }
}
