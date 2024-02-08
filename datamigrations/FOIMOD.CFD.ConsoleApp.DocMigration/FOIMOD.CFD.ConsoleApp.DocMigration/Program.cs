// See https://aka.ms/new-console-template for more information
using Amazon.Runtime;
using Amazon.S3;
using FOIMOD.CFD.DocMigration.BAL;
using FOIMOD.CFD.DocMigration.Models;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;
using System.Data.Odbc;
using System.Net;

Console.WriteLine("Starting, CFD Document Migration!");

#if DEBUG
var configurationbuilder = new ConfigurationBuilder()
                       .AddJsonFile($"appsettings.dev.json", true, true)
                       .AddEnvironmentVariables().Build();
#else
var configurationbuilder = new ConfigurationBuilder()
                       .AddJsonFile($"appsettings.json", true, true)
                       .AddEnvironmentVariables().Build();

#endif

Syncfusion.Licensing.SyncfusionLicenseProvider.RegisterLicense("License here");
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

SystemSettings.FOIFLOWConnectionString = configurationbuilder.GetSection("FOIFLOWConfiguration:FOIFLOWConnectionString").Value;

SystemSettings.CorrespondenceLogMigration = Convert.ToBoolean(configurationbuilder.GetSection("S3Configuration:CorrespondenceLogMigration").Value);
SystemSettings.RecordsMigration = Convert.ToBoolean(configurationbuilder.GetSection("S3Configuration:RecordsMigration").Value);
SystemSettings.MinistryRecordsBucket = configurationbuilder.GetSection("S3Configuration:MinistryRecordsBucket").Value;

SqlConnection axissqlConnection = new SqlConnection(SystemSettings.AXISConnectionString);
OdbcConnection odbcConnection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);

AWSCredentials s3credentials = new BasicAWSCredentials(SystemSettings.S3_AccessKey, SystemSettings.S3_SecretKey);

AmazonS3Config config = new()
{
    ServiceURL = SystemSettings.S3_EndPoint

};

AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);

CorrespondenceLogMigration correspondenceLogMigration = new CorrespondenceLogMigration(axissqlConnection, odbcConnection, amazonS3Client);
correspondenceLogMigration.RequestsToMigrate = SystemSettings.RequestToMigrate;
await correspondenceLogMigration.RunMigration();