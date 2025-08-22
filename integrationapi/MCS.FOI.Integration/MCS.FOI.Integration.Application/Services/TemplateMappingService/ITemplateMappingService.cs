namespace MCS.FOI.Integration.Application.Services.TemplateService
{
    public interface ITemplateMappingService
    {
        Task<IEnumerable<TemplateFieldMappingDto>> GenerateFieldsMapping(int foiRequestId, int foiMinistryRequestId);
    }
}
