using HealthChecks.UI.Client;
using MCS.FOI.Integration.Application.Exceptions.Handler;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.AspNetCore.ResponseCompression;
using Microsoft.Extensions.Configuration;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json;
using Syncfusion.EJ2.SpellChecker;
using System.Reflection;
using System.Security.Claims;

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
            services.AddHttpContextAccessor();


            #region Register JWT Authentication
            var corsOrigin = configuration.GetValue<string>("JWTAuth:CORSORIGINS");
            if (!String.IsNullOrEmpty(corsOrigin))
            {
                string[] _origins = corsOrigin.Split(",");
                services.AddCors(options =>
                                    options.AddPolicy("FOIOrigins", p => p.WithOrigins(_origins)
                                                   .WithMethods("GET", "POST")
                                                   .AllowAnyHeader()
                                                   .AllowAnyMethod()
                                       ));
            }

            services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
            })
            .AddJwtBearer(o =>
            {
                var JWT_OIDC_ISSUER = configuration.GetValue<string>("JWTAuth:JWT_OIDC_ISSUER");
                var JWT_OIDC_AUDIENCE = configuration.GetValue<string>("JWTAuth:JWT_OIDC_AUDIENCE");

                o.Authority = JWT_OIDC_ISSUER;
                o.Audience = JWT_OIDC_AUDIENCE;
                o.RequireHttpsMetadata = false;

                o.Events = new JwtBearerEvents
                {
                    OnTokenValidated = async context =>
                    {
                        var groupsClaims = context.Principal?.FindAll("groups")?.Select(c => c.Value).ToList();
                        if (groupsClaims != null && groupsClaims.Count > 0)
                        {
                            var claimsIdentity = context.Principal?.Identity as ClaimsIdentity;
                            if (claimsIdentity != null)
                            {
                                foreach (var group in groupsClaims)
                                {
                                    claimsIdentity.AddClaim(new Claim("groups", group));
                                }
                            }

                            var emailClaim = claimsIdentity.FindFirst(ClaimTypes.Email);
                            if (emailClaim == null)
                            {
                                var email = context.Principal?.FindFirst("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress")?.Value;
                                if (!string.IsNullOrEmpty(email))
                                {
                                    claimsIdentity.AddClaim(new Claim(ClaimTypes.Email, email));
                                }
                            }
                        }

                        await Task.CompletedTask;
                    },
                    OnAuthenticationFailed = c =>
                    {
                        c.NoResult();
                        c.Response.StatusCode = 500;
                        c.Response.ContentType = "text/plain";
                        return c.Response.WriteAsync("An error occurred processing your authentication.");
                    }
                };
            });

            var iaoGroupsString = configuration.GetValue<string>("JWTAuth:IAOGroups");
            if (!string.IsNullOrWhiteSpace(iaoGroupsString))
            {
                string[] iaoGroups = iaoGroupsString.Split(',').Select(group => group.Trim()).ToArray();

                if (iaoGroups.Length > 0)
                {
                    services.AddAuthorization(options =>
                    {
                        options.AddPolicy("IAOTeam", policy => policy.RequireClaim("groups", iaoGroups));
                    });
                }
            }

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
                    Title = "MCS.FOI.IntegrationAPI",
                    Version = "v1",
                    Description = "API Documentation for FOI Template Integration",
                });

                options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme()
                {
                    Name = "Authorization",
                    Type = SecuritySchemeType.ApiKey,
                    Scheme = "Bearer",
                    BearerFormat = "JWT",
                    In = ParameterLocation.Header,
                    Description = "JWT Authorization header using the Bearer scheme. \r\n\r\n Enter 'Bearer' [space] and then your token in the text input below.\r\n\r\nExample: \"Bearer 1safsfsdfdfd\"",
                });
                options.AddSecurityRequirement(new OpenApiSecurityRequirement {
                    {
                        new OpenApiSecurityScheme {
                            Reference = new OpenApiReference {
                                Type = ReferenceType.SecurityScheme,
                                    Id = "Bearer"
                            }
                        },
                        new string[] {}
                    }
                });

                options.ResolveConflictingActions(apiDescriptions => apiDescriptions.First());
            });
            #endregion

            services.AddHealthChecks()
                .AddNpgSql(configuration.GetConnectionString("DBConnection")!, name: "Postgres")
                .AddRedis(configuration.GetConnectionString("Redis")!, name: "Redis");

            services.AddExceptionHandler<GlobalExceptionHandler>();

            #region DocumentEditor
            var env = builder.Environment;
            var path = configuration.GetValue<string>("SPELLCHECK_DICTIONARY_PATH");
            var jsonFileName = configuration.GetValue<string>("SPELLCHECK_JSON_FILENAME");

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
            var syncfusionLicense = app.Configuration.GetValue<string>("SyncfusionLicense");
            Syncfusion.Licensing.SyncfusionLicenseProvider.RegisterLicense(syncfusionLicense);

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
            app.UseRouting();

            app.UseCors("FOIOrigins");

            app.UseAuthentication();
            app.UseAuthorization();
            app.UseResponseCompression();

            app.MapControllers().RequireCors("FOIOrigins");

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