using System.Runtime.Serialization;

namespace MCS.FOI.AXISIntegration.DataModels
{

    [DataContract]
    public class AXISRequestPageCount
    {
        [DataMember(Name = "id")]
        public string AXISRequestID { get; set; }

        [DataMember]
        public PageCount PageCountInfo { get; set; }
    }

    [DataContract]
    public class PageCount
    {
        [DataMember(Name = "requestpagepount")]
        public int RequestPageCount { get; set; }

        [DataMember(Name = "lanpagepount")]
        public int LANPageCount { get; set; }
    }

}
