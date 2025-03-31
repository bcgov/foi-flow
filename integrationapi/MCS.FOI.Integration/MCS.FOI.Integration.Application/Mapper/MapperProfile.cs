namespace MCS.FOI.Integration.Application.Mapper
{
    public class MapperProfile: Profile
    {
        public MapperProfile() 
        {
            CreateMap<GetCorrespondenceRequest, GetCorrespondenceCommand>().ReverseMap();
            CreateMap<TemplateDto, TemplateResult>().ReverseMap();
        }
    }
}
