using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Serilog;
using System.IO;

namespace MCS.FOI.AXISIntegrationWebAPI
{
    public class Program
    {
        public static IConfiguration Configuration { get; private set; }
        public static void Main(string[] args)
        {
            // Build Configuration
            Configuration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", false, true)               
                .AddCommandLine(args)
                .AddEnvironmentVariables()
                .Build();


           

            // Configure serilog
            Log.Logger = new LoggerConfiguration()
                .ReadFrom.Configuration(Configuration)
                .Enrich.FromLogContext()                
                .Enrich.WithMachineName()                
                .CreateLogger();

            Log.Information("AXIS API started");

            CreateHostBuilder(args)
               .Build().Run();

        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>

            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>()
                    .UseConfiguration(Configuration)
                    .UseSerilog();


                });
    }
}
