using System.Runtime.Serialization;

namespace MCS.FOI.AXISIntegration.DataModels
{
    [DataContract]
    public class Extension
    {
        /// <summary>
        /// THIS EXTENSION POCO Class will have more prop.
        /// </summary>
        public string Type { get; set; }
        [DataMember(Name = "extensionreason")]
        public string Reason { get; set; }

        [DataMember(Name = "extensionreasonid")]
        public int ReasonId { get; set; }

        [DataMember(Name = "extendedduedays")]
        public int ExtendedDueDays { get; set; }

        [DataMember(Name = "extendedduedate")]
        public string ExtendedDueDate { get; set; }

        [DataMember(Name = "extensionstatus")]
        public string Status { get; set; }

        [DataMember(Name = "extensionstatusid")]
        public int StatusId { get; set; }

        [DataMember(Name = "approvednoofdays")]
        public int ApprovedDueDays { get; set; }

        [DataMember(Name = "approveddate")]
        public string ApprovedDate { get; set; }

        [DataMember(Name = "denieddate")]
        public string DeniedDate { get; set; }
        

        //extensionreasonid, extendedduedays, extededduedate,extensionstatusid -- PB/OIPC - P
        //extensionreasonid, extendedduedays, extededduedate,extensionstatusid, approveddate, approvednoofdays, documents:[] -- OIPC - A
        //extensionreasonid, extendedduedays, extededduedate,extensionstatusid, denieddate, documents:[] -- OIPC - D

    }
}
