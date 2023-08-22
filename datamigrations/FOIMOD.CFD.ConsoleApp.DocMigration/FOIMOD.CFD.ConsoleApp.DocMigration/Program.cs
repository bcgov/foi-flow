// See https://aka.ms/new-console-template for more information
using FOIMOD.CFD.DocMigration.BAL;
using FOIMOD.CFD.DocMigration.Models;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;

Console.WriteLine("Starting, CFD Document Migration!");
var configurationbuilder = new ConfigurationBuilder()
                       .AddJsonFile($"appsettings.json", true, true)
                       .AddEnvironmentVariables().Build();


SystemSettings.FileServerRoot = configurationbuilder.GetSection("S3Configuration:FileServerRoot").Value;
SystemSettings.CorrespondenceLogBaseFolder = configurationbuilder.GetSection("S3Configuration:CorrespondenceLogBaseFolder").Value;
SystemSettings.RecordsbaseFolder = configurationbuilder.GetSection("S3Configuration:RecordsbaseFolder").Value;
SystemSettings.S3_AccessKey = configurationbuilder.GetSection("S3Configuration:AWS_accesskey").Value;
SystemSettings.S3_SecretKey = configurationbuilder.GetSection("S3Configuration:AWS_secret").Value;
SystemSettings.S3_EndPoint = configurationbuilder.GetSection("S3Configuration:AWS_S3_Url").Value;
SystemSettings.S3_Attachements_BasePath = configurationbuilder.GetSection("S3Configuration:S3_Attachements_BasePath").Value;
SystemSettings.S3_Attachements_Bucket = configurationbuilder.GetSection("S3Configuration:S3_Attachements_Bucket").Value;
SystemSettings.AttachmentTag = configurationbuilder.GetSection("S3Configuration:AttachmentTag").Value;

SystemSettings.AXISConnectionString = configurationbuilder.GetSection("AXISConfiguration:SQLConnectionString").Value;
SystemSettings.RequestToMigrate = configurationbuilder.GetSection("AXISConfiguration:RequestToMigrate").Value;



SqlConnection axissqlConnection = new SqlConnection(SystemSettings.AXISConnectionString);

CorrespondenceLogMigration correspondenceLogMigration = new CorrespondenceLogMigration(axissqlConnection, null, null);
correspondenceLogMigration.RequestsToMigrate = SystemSettings.RequestToMigrate;
await correspondenceLogMigration.RunMigration();