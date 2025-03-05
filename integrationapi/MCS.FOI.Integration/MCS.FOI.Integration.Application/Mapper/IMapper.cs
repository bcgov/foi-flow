namespace MCS.FOI.Integration.Application.Mapper
{
    public static class IMap
    {
        public static readonly IMapper Mapper;

        static IMap()
        {
            var config = new MapperConfiguration(cfg =>
            {
                cfg.ShouldMapProperty = property => property.GetMethod.IsPublic || property.GetMethod.IsAssembly;
                cfg.AddProfile<MapperProfile>();
            });
            Mapper = config.CreateMapper();
        }
    }
}
