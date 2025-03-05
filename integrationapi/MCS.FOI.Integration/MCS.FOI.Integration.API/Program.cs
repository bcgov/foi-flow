using MCS.FOI.Integration.API;
using MCS.FOI.Integration.Application;
using MCS.FOI.Integration.Infrastructure;
using MCS.FOI.Integration.Infrastructure.Extensions;

var builder = WebApplication.CreateBuilder(args);

// Add CORS services and define a CORS policy
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAnyOrigin",
        builder =>
        {
            builder.AllowAnyOrigin()
                   .AllowAnyHeader()
                   .AllowAnyMethod();
        });
});
builder.Configuration.AddEnvironmentVariables();

builder.Services
    .AddApplicationServices()
    .AddInfrastructureServices(builder.Configuration)
    .AddApiServices(builder);

var app = builder.Build();

// Use the defined CORS policy
app.UseCors("AllowAnyOrigin");

await app.ConfigureMigrationAsync(builder);

app.Configure();

await app.RunAsync();
