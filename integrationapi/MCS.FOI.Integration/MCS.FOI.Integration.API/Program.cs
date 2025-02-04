using MCS.FOI.Integration.API;
using MCS.FOI.Integration.Application;
using MCS.FOI.Integration.Infrastructure;
using MCS.FOI.Integration.Infrastructure.Extensions;

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddApplicationServices()
    .AddInfrastructureServices(builder.Configuration)
    .AddApiServices(builder.Configuration);

builder.Configuration.AddEnvironmentVariables();

var app = builder.Build();

await app.ConfigureMigrationAsync(builder);

app.Configure();


await app.RunAsync();
