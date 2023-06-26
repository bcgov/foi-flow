using MCS.FOI.AXISIntegration.Utilities.Types;

namespace MCS.FOI.AXISIntegration.Utilities.Interfaces
{
    public interface IFOIFlowConnection
    {
        /// <summary>
        /// FOI FLOW Development  environment DB connection string
        /// </summary>
        public string FOIPGDevelopmentConnection { get; set; }
        /// <summary>
        /// FOI FLOW Production environment connection string
        /// </summary>        
        public string FOIPGProductionConnection { get; set; }
        /// <summary>
        /// FOI FLOW Test environment connection string
        /// </summary>
        public string FOIPGTestConnection { get; set; }
        /// <summary>
        /// FOI FLOW Current environment
        /// </summary>
        public Environments Environment { get; set; }

    }
}
