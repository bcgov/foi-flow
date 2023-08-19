// See https://aka.ms/new-console-template for more information
using FOIMOD.CFD.DocMigration.Models;
using Microsoft.Extensions.Configuration;

Console.WriteLine("Starting, CFD Document Migration!");
var configurationbuilder = new ConfigurationBuilder()
                       .AddJsonFile($"appsettings.json", true, true)
                       .AddEnvironmentVariables().Build();

SystemSettings.S3_AccessKey = configurationbuilder.GetSection("S3Configuration:AWS_accesskey").Value;
SystemSettings.S3_SecretKey = configurationbuilder.GetSection("S3Configuration:AWS_secret").Value;
SystemSettings.S3_EndPoint = configurationbuilder.GetSection("S3Configuration:AWS_S3_Url").Value;
SystemSettings.AXISConnectionString = configurationbuilder.GetSection("AXISConfiguration:SQLConnectionString").Value;
SystemSettings.RequestToMigrate = configurationbuilder.GetSection("AXISConfiguration:RequestToMigrate").Value;