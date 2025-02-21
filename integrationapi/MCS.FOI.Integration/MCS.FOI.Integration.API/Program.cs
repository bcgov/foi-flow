using MCS.FOI.Integration.API;
using MCS.FOI.Integration.Application;
using MCS.FOI.Integration.Infrastructure;
using MCS.FOI.Integration.Infrastructure.Extensions;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration
    //.SetBasePath(builder.Environment.ContentRootPath)
    //.AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
    //.AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true)
    .AddEnvironmentVariables();

builder.Services
    .AddApplicationServices()
    .AddInfrastructureServices(builder.Configuration)
    .AddApiServices(builder);

var app = builder.Build();

await app.ConfigureMigrationAsync(builder);

app.Configure();

await app.RunAsync();
