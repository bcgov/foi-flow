using MCS.FOI.AXISIntegration.Utilities.Types;
using Microsoft.Extensions.Configuration;
using System;
using System.IO;

namespace MCS.FOI.AXISIntegration.Utilities
{
    public class SettingsManager
    {

        /// <summary>
        /// Configuration file name to read from.
        /// </summary>
        public static string ConfigurationFileName { get; set; } = "appsettings.json";
        
        /// <summary>
        /// Must be first call to obtain properties
        /// </summary>
        public static void Initializer()
        {

            InitConfiguration();

            var setting = InitOptions<ConnectionStrings>("ConnectionStrings");

            DevelopmentConnectionString = setting.DevelopmentConnection;
            TestConnectionString = setting.TestConnection;
            ProductionConnectionString = setting.ProductionConnection;

            Environment = setting.Environment;

            ConnectionString = AssignConnectionString(Environment);
            
        }
        /// <summary>
        /// Assign connection string by Environment from appsettings.json
        /// </summary>
        /// <param name="environment"><see cref="Environment"/></param>
        /// <returns>Current connection string from Environment</returns>
        private static string AssignConnectionString(Environments environment) => environment switch
        {
            Environments.Production => ProductionConnectionString,
            Environments.Test => TestConnectionString,
            Environments.Development => DevelopmentConnectionString,
            _ => throw new ArgumentOutOfRangeException(nameof(environment), environment, null)
        };

        /// <summary>
        /// Development connection string
        /// </summary>
        public static string DevelopmentConnectionString { get; set; }
        /// <summary>
        /// Test connection string
        /// </summary>
        public static string TestConnectionString { get; set; }
        /// <summary>
        /// Prod connection string
        /// </summary>
        public static string ProductionConnectionString { get; set; }
        /// <summary>
        /// Current connection string
        /// </summary>
        public static string ConnectionString { get; set; }
        /// <summary>
        /// Current environment
        /// </summary>
        public static Environments Environment { get; set; }
        
        /// <summary>
        /// Initialize ConfigurationBuilder for appsettings
        /// </summary>
        /// <returns>IConfigurationRoot</returns>
        private static IConfigurationRoot InitConfiguration()
        {

            var builder = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile(ConfigurationFileName);

            return builder.Build();

        }

        /// <summary>
        /// Generic method to read a section from the json configuration file.
        /// </summary>
        /// <typeparam name="T">Class type</typeparam>
        /// <param name="section">Section to read</param>
        /// <returns>Instance of T</returns>
        public static T InitOptions<T>(string section) where T : new()
        {
            var config = InitConfiguration();
            return config.GetSection(section).Get<T>();
        }
    }
}
