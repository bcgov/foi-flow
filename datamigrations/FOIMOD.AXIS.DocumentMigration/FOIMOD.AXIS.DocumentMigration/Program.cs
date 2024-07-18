// See https://aka.ms/new-console-template for more information
using Amazon.Runtime;
using Amazon.S3;
using FOIMOD.HistoricalDocMigration.DocMigration.BAL;
using FOIMOD.HistoricalDocMigration.Models;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Data.Odbc;


Console.WriteLine("Starting, CFD Document Migration!");

#if DEBUG
var configurationbuilder = new ConfigurationBuilder()
                       .AddJsonFile($"appsettings.json", true, true)
                       .AddEnvironmentVariables().Build();
#else
var configurationbuilder = new ConfigurationBuilder()
                       .AddJsonFile($"appsettings.json", true, true)
                       .AddEnvironmentVariables().Build();

#endif



//Define the path to the text file
string logFilePath = string.Format("console_log_{0}.txt", DateTime.Now.ToShortDateString());

//Create a StreamWriter to write logs to a text file
using (StreamWriter logFileWriter = new StreamWriter(logFilePath, append: true))
{
    //Create an ILoggerFactory
    ILoggerFactory loggerFactory = LoggerFactory.Create(builder =>
    {
        //Add console output
        builder.AddSimpleConsole(options =>
        {
            options.IncludeScopes = true;
            options.SingleLine = true;
            options.TimestampFormat = "HH:mm:ss ";
        });

        //Add a custom log provider to write logs to text files
        builder.AddProvider(new CustomFileLoggerProvider(logFileWriter));
    });

    //Create an ILogger
    ILogger<Program> logger = loggerFactory.CreateLogger<Program>();

    // Output some text on the console
    using (logger.BeginScope("[scope is enabled]"))
    {



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
        SystemSettings.FOIDocReviewerConnectionString = configurationbuilder.GetSection("FOIFLOWConfiguration:FOIDocumentReviewerString").Value;

        SystemSettings.CorrespondenceLogMigration = Convert.ToBoolean(configurationbuilder.GetSection("S3Configuration:CorrespondenceLogMigration").Value);
        SystemSettings.RecordsMigration = Convert.ToBoolean(configurationbuilder.GetSection("S3Configuration:RecordsMigration").Value);
        SystemSettings.MinistryRecordsBucket = configurationbuilder.GetSection("S3Configuration:MinistryRecordsBucket").Value;
        SystemSettings.SyncfusionLicense = configurationbuilder.GetSection("S3Configuration:SyncfusionLicense").Value;

        Syncfusion.Licensing.SyncfusionLicenseProvider.RegisterLicense(SystemSettings.SyncfusionLicense);

        SqlConnection axissqlConnection = new SqlConnection(SystemSettings.AXISConnectionString);
        OdbcConnection odbcConnection = new OdbcConnection(SystemSettings.FOIFLOWConnectionString);
        OdbcConnection docreviewerconnection = new OdbcConnection(SystemSettings.FOIDocReviewerConnectionString);

        AWSCredentials s3credentials = new BasicAWSCredentials(SystemSettings.S3_AccessKey, SystemSettings.S3_SecretKey);

        AmazonS3Config config = new()
        {
            ServiceURL = SystemSettings.S3_EndPoint

        };

        AmazonS3Client amazonS3Client = new AmazonS3Client(s3credentials, config);
        
        Console.WriteLine("Migration process Starting....");

        if (SystemSettings.CorrespondenceLogMigration)
        {
            Console.WriteLine("CorrespondenceLogMigration  Starting...");
            CorrespondenceLogMigration correspondenceLogMigration = new CorrespondenceLogMigration(axissqlConnection, odbcConnection, amazonS3Client, logger);
            correspondenceLogMigration.RequestsToMigrate = SystemSettings.RequestToMigrate;
            await correspondenceLogMigration.RunMigration();
            Console.WriteLine("CorrespondenceLogMigration  Completed");
        }

        if (SystemSettings.RecordsMigration)
        {
            Console.WriteLine("RecordsMigration  Starting...");
            RecordsLogMigration recordsLogMigration = new RecordsLogMigration(axissqlConnection, odbcConnection, amazonS3Client, logger);
            recordsLogMigration.RequestsToMigrate = SystemSettings.RequestToMigrate;
            await recordsLogMigration.RunMigration();
            Console.WriteLine("RecordsMigration  Completed");
        }

        Console.WriteLine("Migration process over....");
        Console.ReadLine();

    }
}



// Customized ILoggerProvider, writes logs to text files
public class CustomFileLoggerProvider : ILoggerProvider
{
    private readonly StreamWriter _logFileWriter;

    public CustomFileLoggerProvider(StreamWriter logFileWriter)
    {
        _logFileWriter = logFileWriter ?? throw new ArgumentNullException(nameof(logFileWriter));
    }

    public ILogger CreateLogger(string categoryName)
    {
        return new CustomFileLogger(categoryName, _logFileWriter);
    }

    public void Dispose()
    {
        _logFileWriter.Dispose();
    }
}

// Customized ILogger, writes logs to text files
public class CustomFileLogger : ILogger
{
    private readonly string _categoryName;
    private readonly StreamWriter _logFileWriter;

    public CustomFileLogger(string categoryName, StreamWriter logFileWriter)
    {
        _categoryName = categoryName;
        _logFileWriter = logFileWriter;
    }

    public IDisposable BeginScope<TState>(TState state)
    {
        return null;
    }

    public bool IsEnabled(LogLevel logLevel)
    {
        // Ensure that only information level and higher logs are recorded
        return logLevel >= LogLevel.Information;
    }

    public void Log<TState>(
        LogLevel logLevel,
        EventId eventId,
        TState state,
        Exception exception,
        Func<TState, Exception, string> formatter)
    {
        // Ensure that only information level and higher logs are recorded
        if (!IsEnabled(logLevel))
        {
            return;
        }

        // Get the formatted log message
        var message = formatter(state, exception);

        //Write log messages to text file
        _logFileWriter.WriteLine($"[{logLevel}] [{_categoryName}] {message}");
        _logFileWriter.Flush();
    }
}