using MCS.FOI.Integration.Application.Queries.GetListOptions;

namespace MCS.FOI.Integration.Application.Mapper
{
    public class MapperProfile: Profile
    {
        public MapperProfile() 
        {
            CreateMap<TemplateFieldMapping, TemplateFieldMappingDto>().ReverseMap();
            CreateMap<TemplateListOptions, ListOptionsResult>().ReverseMap();
            CreateMap<Core.Entities.Template, TemplateResult>().ReverseMap();
        }
    }
}
