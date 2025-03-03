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
        Task<IEnumerable<ApplicantCategoryDto>> GetApplicantCategory(int? applicantCategoryId);
        Task<FOIRequestCFRFeesDto> GetApprovedCRFFee(int? ministryRequestId);
        Task<FOIRequestPaymentDto> GetPayment(int? foiRequestId, int? ministryRequestId);
        Task<IEnumerable<FOIRequestOIPCDto>> GetFOIRequestOIPC(int? ministryRequestId, int versionId);
        Task<IEnumerable<OperatingTeamEmailsDto>> GetOperatingTeamEmails(string? operatingTeamName);
        Task<IEnumerable<FOIRequestExtensionsDto>> GetFOIRequestExtensions(int? ministryRequestId, int? ministryRequestVersionId);
        Task<IEnumerable<PaymentDto>> GetPaymentFees(int foiRequestId);
        Task<FOIRequestCFRFeesDto> GetCRFFee(int? ministryRequestId);
        Task<IEnumerable<FOIRequestExtensionsDto>> GetExtensions(int? ministryRequestId, int? ministryRequestVersionId);
        Task<FOIMinistryRequestDto> GetRequestOriginalDueDate(int foiMinistryRequestId);
        Task<IEnumerable<ReceivedModesDto>> GetReceivedModes(int receivedModeId);
        Task<IEnumerable<SubjectCodeDto>> GetMinistryRequestSubjectCodes(int ministryRequestId, int versionId);
        Task<IEnumerable<FOIRequestPersonalAttributeDto>> GetRequestPersonalAttributes(int foiRequestId, int version);
        Task<IEnumerable<FOIOpenInformationRequestsDto>> GetOpenInformationRequests(int ministryRequestId, int versionId);
        Task<IEnumerable<FOIRawRequestDTO>> GetRawRequest(int foiRequestId);
    }
}
