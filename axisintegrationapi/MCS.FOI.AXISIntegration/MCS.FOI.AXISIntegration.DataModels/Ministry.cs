using System.Runtime.Serialization;

namespace MCS.FOI.AXISIntegration.DataModels
{
    [DataContract]
    public class Ministry
    {
        /// <summary>
        /// THIS EXTENSION POCO Class will have more prop.
        /// </summary>

        [DataMember(Name = "code")]
        public string Code { get; set; }

        public Ministry(string code)
        {
            Code = code;
        }
    }
}
