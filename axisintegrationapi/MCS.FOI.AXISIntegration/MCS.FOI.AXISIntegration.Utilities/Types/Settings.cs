namespace MCS.FOI.AXISIntegration.Utilities.Types
{
    /// <summary>
    /// High level container for creating and reading a configuration file
    /// </summary>
    public class Settings
    {
        public ConnectionStrings ConnectionStrings { get; set; }

        public FOIFlowConnectionStrings FOIFlowConnectionStrings { get; set; }
    }
}
