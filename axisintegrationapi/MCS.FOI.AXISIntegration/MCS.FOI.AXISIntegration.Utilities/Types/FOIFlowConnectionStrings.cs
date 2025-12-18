using MCS.FOI.AXISIntegration.Utilities.Interfaces;
using System;

namespace MCS.FOI.AXISIntegration.Utilities.Types
{
    /// <summary>
    /// FOI FLOW PG Db connection strings
    /// </summary>
    public class FOIFlowConnectionStrings : IFOIFlowConnection
    {
       
        public string FOIPGDevelopmentConnection { get; set; }
        public string FOIPGProductionConnection { get; set; }
        public string FOIPGTestConnection { get; set; }
        public Environments Environment { get; set; }

        public override string ToString() => Environment.ToString();

    }
}