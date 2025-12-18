using MCS.FOI.AXISIntegration.Utilities.Types;

namespace MCS.FOI.AXISIntegration.Utilities.Interfaces
{
    public interface IConnection
    {
        /// <summary>
        /// AXIS Development  environment DB connection string
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
        /// <summary>
        /// AXIS Current environment
        /// </summary>
        public Environments Environment { get; set; }

    }
}
