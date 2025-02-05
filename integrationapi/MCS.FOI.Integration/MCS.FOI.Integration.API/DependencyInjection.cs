using FluentValidation;
using HealthChecks.UI.Client;
using MCS.FOI.Integration.Application.Behaviour;
using MCS.FOI.Integration.Application.Exceptions.Handler;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.OpenApi.Models;
using System.Reflection;

namespace MCS.FOI.Integration.API
{
    public static class DependencyInjection
    {
        public static IServiceCollection AddApiServices(this IServiceCollection services, IConfiguration configuration)
        {
            services.AddControllers();

            // Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
            services.AddEndpointsApiExplorer();

            // Add Endpoints API Explorer and Swagger for API documentation
            services.AddEndpointsApiExplorer();

            services.AddSwaggerGen(options =>
            {
                var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
                var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
                if (File.Exists(xmlPath))
                {
                    options.IncludeXmlComments(xmlPath);
                }

                options.SwaggerDoc("v1", new OpenApiInfo
                {
                    Title = "FOI Integration",
                    Version = "v1",
                    Description = "API Documentation for FOI Template Integration",
                });

                options.ResolveConflictingActions(apiDescriptions => apiDescriptions.First());
            });

            services.AddHealthChecks()
                .AddNpgSql(configuration.GetConnectionString("DBConnection")!, name: "Postgres")
                .AddRedis(configuration.GetConnectionString("Redis")!, name: "Redis");

            services.AddExceptionHandler<GlobalExceptionHandler>();
            // Register JWT Authentication
            // here

            return services;
        }

        public static WebApplication Configure(this WebApplication app)
        {
            if (app.Environment.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
                app.UseSwagger();
                app.UseSwaggerUI(c =>
                    c.SwaggerEndpoint("/swagger/v1/swagger.json", "FOI Integration.API"));
            }
            else
            {
                app.UseExceptionHandler(errorApp =>
                {
                    errorApp.Run(async context =>
                    {
                        var exceptionHandlerFeature = context.Features.Get<IExceptionHandlerFeature>();
                        if (exceptionHandlerFeature != null)
                        {
                            var logger = context.RequestServices.GetRequiredService<ILogger<Program>>();
                            logger.LogError(exceptionHandlerFeature.Error, "An unhandled exception occurred.");
                        }

                        context.Response.StatusCode = 500;
                        context.Response.ContentType = "application/json";
                        var errorResponse = new { Message = "An unexpected fault occurred. Please try again later." };
                        await context.Response.WriteAsJsonAsync(errorResponse);
                    });
                });
            }

            app.UseHttpsRedirection();
            //app.UseRouting();

            //app.UseAuthentication();
            app.UseAuthorization();

            app.MapControllers();
            app.MapHealthChecks("/health", new HealthCheckOptions
            {
                Predicate = _ => true,
                ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
            });

            app.UseExceptionHandler(options => { });

            return app;
        }
    }
}