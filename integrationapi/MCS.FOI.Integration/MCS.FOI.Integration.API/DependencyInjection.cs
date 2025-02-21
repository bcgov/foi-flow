using HealthChecks.UI.Client;
using MCS.FOI.Integration.Application.Exceptions.Handler;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.AspNetCore.ResponseCompression;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json;
using Syncfusion.EJ2.SpellChecker;
using System.Reflection;

namespace MCS.FOI.Integration.API
{
    public static class DependencyInjection
    {
        public static IServiceCollection AddApiServices(this IServiceCollection services, WebApplicationBuilder builder)
        {
            var configuration = builder.Configuration;

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

            #region Register JWT Authentication
            // here
            #endregion

            #region DocumentEditor
            var env = builder.Environment;
            var path = configuration["SPELLCHECK_DICTIONARY_PATH"];
            var jsonFileName = configuration["SPELLCHECK_JSON_FILENAME"];

            // Check and set default paths
            path = string.IsNullOrEmpty(path) ? Path.Combine(env.ContentRootPath, "App_Data") : Path.Combine(env.ContentRootPath, path);
            jsonFileName = string.IsNullOrEmpty(jsonFileName) ? Path.Combine(path, "spellcheck.json") : Path.Combine(path, jsonFileName);

            if (File.Exists(jsonFileName))
            {
                var jsonImport = File.ReadAllText(jsonFileName);
                Console.WriteLine($"jsonImport: {jsonImport}");
                var spellChecks = JsonConvert.DeserializeObject<List<DictionaryData>>(jsonImport);
                var spellDictCollection = new List<DictionaryData>();
                string personalDictPath = null;

                if (spellChecks != null)
                {
                    foreach (var spellCheck in spellChecks)
                    {
                        spellDictCollection.Add(new DictionaryData(spellCheck.LanguadeID, Path.Combine(path, spellCheck.DictionaryPath), Path.Combine(path, spellCheck.AffixPath)));
                        personalDictPath = Path.Combine(path, spellCheck.PersonalDictPath);
                        Console.WriteLine($"spellCheck.LanguadeID: {spellCheck.LanguadeID}");
                        Console.WriteLine($"spellCheck.DictionaryPath: {spellCheck.DictionaryPath}");
                        Console.WriteLine($"personalDictPath: {personalDictPath}");
                    }
                }
                SpellChecker.InitializeDictionaries(spellDictCollection, personalDictPath, 3);
            }

            services.Configure<GzipCompressionProviderOptions>(options => options.Level = System.IO.Compression.CompressionLevel.Optimal);
            services.AddResponseCompression();
            #endregion

            return services;
        }

        public static WebApplication Configure(this WebApplication app)
        {
            // Register Syncfusion license
            Syncfusion.Licensing.SyncfusionLicenseProvider.RegisterLicense(app.Configuration["SyncfusionLicense"]);

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
            app.UseResponseCompression();

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