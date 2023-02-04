using MCS.FOI.AXISIntegration.DAL;
using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.Utilities;
using MCS.FOI.AXISIntegrationWebAPI.Controllers;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.OpenApi.Models;
using System;

namespace MCS.FOI.AXISIntegrationWebAPI
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            SettingsManager.AuthConnectionInitializer();

            if (!String.IsNullOrEmpty(SettingsManager.CORSORIGINS))
            {
                string[] _origins = SettingsManager.CORSORIGINS.Split(",");
                services.AddCors(options =>
                                    options.AddPolicy("FOIOrigins", p => p.WithOrigins(_origins)
                                                   .WithMethods("GET")
                                                   .AllowAnyHeader()
                                                   .AllowAnyMethod()
                                       )) ;
            }

            services.AddScoped<IRequestDA, RequestsDA>();

            var serviceProvider = services.BuildServiceProvider();            
            var requestlogger = serviceProvider.GetService<ILogger<RequestSearchController>>();
            services.AddSingleton(typeof(ILogger), requestlogger);
            services.AddScoped<IRequestDA, RequestsDA>();
            services.AddScoped<IFOIFlowRequestUserDA,FOIFlowRequestUsersDA>();
            

            services.AddControllers();

            // Configure JWT authentication.
            services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;

            }).AddJwtBearer(o =>
            {
                o.Authority = SettingsManager.JWT_OIDC_ISSUER;
                o.Audience = SettingsManager.JWT_OIDC_AUDIENCE;
                o.RequireHttpsMetadata = false;

                o.Events = new JwtBearerEvents()
                {
                    OnAuthenticationFailed = c =>
                    {
                        c.NoResult();

                        c.Response.StatusCode = 500;
                        c.Response.ContentType = "text/plain";

                        return c.Response.WriteAsync("An error occured processing your authentication.");
                    }
                };
            });

            if (!String.IsNullOrEmpty(SettingsManager.IAOGroups))
            {
                string[] iaogroups = SettingsManager.IAOGroups.Split(",");
                services.AddAuthorization(options =>
                {
                    options.AddPolicy("IAOTeam", policy => policy.RequireClaim("groups", iaogroups));

                });
            }

            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "MCS.FOI.AXISIntegrationWebAPI", Version = "v1" });
                c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme()
                {
                    Name = "Authorization",
                    Type = SecuritySchemeType.ApiKey,
                    Scheme = "Bearer",
                    BearerFormat = "JWT",
                    In = ParameterLocation.Header,
                    Description = "JWT Authorization header using the Bearer scheme. \r\n\r\n Enter 'Bearer' [space] and then your token in the text input below.\r\n\r\nExample: \"Bearer 1safsfsdfdfd\"",
                });
                c.AddSecurityRequirement(new OpenApiSecurityRequirement {
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

            });


        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();

            }
            app.UseStaticFiles();
            app.UseSwagger();
            app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "MCS.FOI.AXISIntegrationWebAPI v1"));

            app.UseHttpsRedirection(); 

            app.UseRouting();


            app.UseCors("FOIOrigins");

            app.UseAuthentication();
            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers()
                .RequireCors("FOIOrigins");
            });
        }
    }
}
