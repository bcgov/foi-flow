using MCS.FOI.Integration.Core.Repositories.RedisRepository;
using MCS.FOI.Integration.Infrastructure.Repositories.RedisRepository;

namespace MCS.FOI.Integration.Application
{
    public static class DependencyInjection
    {
        public static IServiceCollection AddApplicationServices(this IServiceCollection services)
        {
            services.AddHttpClient();
            services.AddAutoMapper(Assembly.GetExecutingAssembly());

            var assembly = Assembly.GetExecutingAssembly();
            services.AddMediatR(config =>
            {
                config.RegisterServicesFromAssembly(assembly);
                config.AddOpenBehavior(typeof(ValidationBehavior<,>));
                config.AddOpenBehavior(typeof(LoggingBehavior<,>));
            });

            services.AddValidatorsFromAssembly(assembly);

            #region Command Handler Injection
            services.AddScoped<ICommandHandler<GetCorrespondenceCommand, string>, GetCorrespondenceCommandHandler>();
            services.AddScoped<ICommandHandler<UpdateTemplateCacheCommand, bool>, UpdateTemplateCacheCommandHandler>();
            #endregion

            #region Query Handler Injection
            services.AddScoped<IQueryHandler<GetTemplatesQuery, IEnumerable<TemplateResult>>, GetTemplatesQueryHandler>();
            #endregion

            #region Service Injection
            services.AddScoped<ITemplateMappingService, TemplateMappingService>();
            services.AddScoped<ITemplateDataService, TemplateDataService>();
            services.AddScoped<IS3ConnectionService, S3ConnectionService>();
            services.AddScoped<ITemplateRedisCacheRepository, TemplateRedisCacheRepository>();
            #endregion

            return services;
        }
    }
}
