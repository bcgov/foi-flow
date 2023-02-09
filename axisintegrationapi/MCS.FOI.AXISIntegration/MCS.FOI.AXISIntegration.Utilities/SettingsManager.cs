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
        public static void DBConnectionInitializer()
        {

            InitConfiguration();

            var setting = InitOptions<ConnectionStrings>("ConnectionStrings");
            var foiflowdbsetting = InitOptions<FOIFlowConnectionStrings>("FOIFlowConnectionStrings");

            DevelopmentConnectionString = setting.DevelopmentConnection;
            TestConnectionString = setting.TestConnection;
            ProductionConnectionString = setting.ProductionConnection;

            FOIFlowDevelopmentConnectionString = foiflowdbsetting.FOIPGDevelopmentConnection;
            FOIFlowTestConnectionString = foiflowdbsetting.FOIPGTestConnection;
            FOIFlowProductionConnectionString = foiflowdbsetting.FOIPGProductionConnection;

            Environment = setting.Environment;
            FOIFlowEnvironment = foiflowdbsetting.Environment;

            ConnectionString = AssignConnectionString(Environment);
            FOIFlowConnectionString = AssignFOIFlowConnectionString(FOIFlowEnvironment);
        }

        public static void AuthConnectionInitializer()
        {
            InitConfiguration();
            var setting = InitOptions<KCAuthentication>("KCAuthentication");

            JWT_OIDC_ISSUER = setting.JWT_OIDC_ISSUER;
            JWT_OIDC_AUDIENCE = setting.JWT_OIDC_AUDIENCE;
            IAOGroups = setting.IAOGroups;
            CORSORIGINS = setting.CORSORIGINS;

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

        private static string AssignFOIFlowConnectionString(Environments environment) => environment switch
        {
            Environments.Production => FOIFlowProductionConnectionString,
            Environments.Test => FOIFlowTestConnectionString,
            Environments.Development => FOIFlowDevelopmentConnectionString,
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


        public static string FOIFlowDevelopmentConnectionString { get; set; }
        public static string FOIFlowTestConnectionString { get; set; }

        public static string FOIFlowProductionConnectionString { get; set; }
        /// <summary>
        /// Current connection string
        /// </summary>
        public static string FOIFlowConnectionString { get; set; }
        /// <summary>
        /// Current environment
        /// </summary>
        public static Environments FOIFlowEnvironment { get; set; }

        public static string JWT_OIDC_WELL_KNOWN_CONFIG { get; set; }

        public static string JWT_OIDC_AUDIENCE { get; set; }

        public static string JWT_OIDC_ISSUER { get; set; }

        public static string JWT_OIDC_ALGORITHMS { get; set; }

        public static string JWT_OIDC_JWKS_URI { get; set; }

        public static string IAOGroups { get; set; }

        public static string CORSORIGINS { get; set; }

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
