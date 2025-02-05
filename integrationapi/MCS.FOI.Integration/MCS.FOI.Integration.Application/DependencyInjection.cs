using MCS.FOI.Integration.Application.Queries.GetListOptions;

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
            #endregion

            #region Query Handler Injection
            services.AddScoped<IQueryHandler<GetTemplatesQuery, IEnumerable<TemplateResult>>, GetTemplatesQueryHandler>();
            services.AddScoped<IQueryHandler<GetListOptionsQuery, IEnumerable<ListOptionsResult>>, GetListOptionsQueryHandler>();
            #endregion

            #region Service Injection
            services.AddScoped<ITemplateMappingService, TemplateMappingService>();
            services.AddScoped<ITemplateDataService, TemplateDataService>();
            services.AddScoped<IS3ConnectionService, S3ConnectionService>();
            #endregion

            return services;
        }
    }
}
