using MCS.FOI.AXISIntegration.Utilities.Interfaces;

namespace MCS.FOI.AXISIntegration.Utilities.Types
{
    /// <summary>
    /// Application connection strings
    /// </summary>
    public class ConnectionStrings : IConnection
    {
        /// <summary>
        /// AXIS Development environment connection string
        /// </summary>
        public string DevelopmentConnection { get; set; }
        /// <summary>
        /// AXIS Production environment connection string
        /// </summary>        
        public string ProductionConnection { get; set; }
        /// <summary>
        /// AXIS Test environment connection string
        /// </summary>
        public string TestConnection { get; set; }

        public Environments Environment { get; set; }


        public override string ToString() => Environment.ToString();

    }
}