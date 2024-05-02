using MCS.FOI.AXISIntegration.DataModels;

namespace MCS.FOI.AXISIntegration.DAL.Interfaces
{
    public interface IRequestDA
    {
        public string GetAXISRequestString(string requestNumber);

        public AXISRequest GetAXISRequest(string request);

        public string GetAXISRequestsPageCountString();

        public string PostAXISRequestsPageCountString(string[] arrayOfRequestId);
    }
}
