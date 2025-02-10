namespace MCS.FOI.Integration.Application.Services.TemplateDataService
{
    public interface ITemplateDataService
    {
        Task<FOIRequestDto> GetRequest(int foiRequestId);
        Task<FOIRequestAssigneeDto> GetAssignee(int foiMinistryRequestId);
        Task<FOIMinistryRequestDto> GetRequestByMinistryRequestId(int foiMinistryRequestId);
        Task<IEnumerable<FOIRequestContactInformationDto>> GetRequestContactInformation(int foiRequestId, int versionId);
        Task<IEnumerable<FOIRequestApplicantInfoDto>> GetRequestApplicantInfos(int foiRequestId, int version, RequestorType requestorTypeId);
        Task<IEnumerable<ProgramAreaDto>> GetProgramArea(int? programAreaId);
        Task<IEnumerable<ProgramAreaDto>> GetProgramAreas();
        Task<IEnumerable<ApplicantCategoryDto>> GetApplicantCategory(int? applicantCategoryId);
        Task<FOIRequestCFRFeesDto> GetApprovedCRFFee(int? ministryRequestId);
        Task<FOIRequestPaymentDto> GetPayment(int? foiRequestId, int? ministryRequestId);
        Task<IEnumerable<FOIRequestOIPCDto>> GetFOIRequestOIPC(int? ministryRequestId, int versionId);
        Task<IEnumerable<OperatingTeamEmailsDto>> GetOperatingTeamEmails(string? operatingTeamName);
        Task<IEnumerable<FOIRequestExtensionsDto>> GetFOIRequestExtensions(int? ministryRequestId, int? ministryRequestVersionId);
        Task<IEnumerable<PaymentDto>> GetPaymentFees(int foiRequestId);
    }
}
