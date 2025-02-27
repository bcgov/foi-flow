namespace MCS.FOI.Integration.Application.Mapper
{
    public class MapperProfile: Profile
    {
        public MapperProfile() 
        {
            CreateMap<TemplateFieldMapping, TemplateFieldMappingDto>().ReverseMap();
            CreateMap<Core.Entities.Template, TemplateResult>().ReverseMap();
            CreateMap<Core.Entities.Template, TemplateDto>().ReverseMap();
        }
    }
}
