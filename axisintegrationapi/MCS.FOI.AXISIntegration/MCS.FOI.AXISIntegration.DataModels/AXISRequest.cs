using System;
using System.Collections.Generic;
using System.Runtime.Serialization;

namespace MCS.FOI.AXISIntegration.DataModels
{
    [DataContract]
    public class AXISRequest
    {

        //MORE PROPERTIES TO ADD HERE. TODO

        [DataMember(Name = "axisRequestId")]
        public string AXISRequestID { get; set; }

        [DataMember(Name = "axisSyncDate")]
        public string AxisSyncDate { get; set; }

        [DataMember(Name = "description")]
        public string RequestDescription { get; set; }
     
        [DataMember(Name = "fromDate")]
        public string RequestDescriptionFromDate { get; set; }

        [DataMember(Name = "toDate")]
        public string RequestDescriptionToDate { get; set; }
       
        [DataMember(Name = "requestType")]
        public string RequestType { get; set; }

        [DataMember(Name = "isRestricted")]
        public bool IsRestricted { get; set; }

        [DataMember(Name = "receivedDate")]
        public string ReceivedDate { get; set; }

        [DataMember(Name = "compareReceivedDate")]
        public string CompareReceivedDate { get; set; }

        [DataMember(Name = "receivedDateUF")]
        public string ReceivedDateUF { get; set; }
       
        [DataMember(Name = "requestProcessStart")]
        public string StartDate { get; set; }

        [DataMember(Name = "dueDate")]
        public string DueDate { get; set; }

        [DataMember(Name = "originalDueDate")]
        public string OriginalDueDate { get; set; }

        [DataMember(Name = "cfrDueDate")]
        public string CFRDueDate { get; set; }

        [DataMember(Name = "category")]
        public string Category { get; set; }
        
        [DataMember(Name = "receivedMode")]
        public string ReceivedMode { get; set; }

        [DataMember(Name = "deliveryMode")]
        public string DeliveryMode { get; set; }

        [DataMember(Name = "ispiiredacted")]
        public bool Ispiiredacted { get; set; }

        [DataMember(Name = "firstName")]
        public string ApplicantFirstName { get; set; }

        [DataMember(Name = "middleName")]
        public string ApplicantMiddleName { get; set; }

        [DataMember(Name = "lastName")]
        public string ApplicantLastName { get; set; }

        

        [DataMember(Name = "businessName")]
        public string BusinessName { get; set; }

        [DataMember(Name = "email")]
        public string Email { get; set; }

        [DataMember(Name = "address")]
        public string Address { get; set; }

        [DataMember(Name = "addressSecondary")]
        public string AddressSecondary { get; set; }

        [DataMember(Name = "city")]
        public string City { get; set; }

        [DataMember(Name = "province")]
        public string Province { get; set; }

        [DataMember(Name = "country")]
        public string Country { get; set; }

        [DataMember(Name = "postal")]
        public string PostalCode { get; set; }

        [DataMember(Name = "phonePrimary")]
        public string PhonePrimary { get; set; }

        [DataMember(Name = "phoneSecondary")]
        public string PhoneSecondary { get; set; }

        [DataMember(Name = "workPhonePrimary")]
        public string WorkPhonePrimary { get; set; }

        [DataMember(Name = "workPhoneSecondary")]
        public string WorkPhoneSecondary { get; set; }
  
        [DataMember(Name = "correctionalServiceNumber")]
        public string CorrectionalServiceNumber { get; set; }

        [DataMember(Name = "publicServiceEmployeeNumber")]
        public string PublicServiceEmployeeNumber { get; set; }

        [DataMember(Name = "requestPageCount")]
        public int RequestPageCount { get; set; }

        [DataMember(Name = "subjectCode")]
        public string SubjectCode { get; set; }

        [DataMember(Name = "selectedMinistries")]
        public List<Ministry> SelectedMinistries { get; set; }
        
        [DataMember(Name = "additionalPersonalInfo")]
        public AdditionalPersonalInformation AdditionalPersonalInfo { get; set; }

        [DataMember(Name = "Extensions")]
        public List<Extension> Extensions { get; set; }

    }

    [DataContract]
    public class AdditionalPersonalInformation
    {
        [DataMember(Name = "birthDate")]
        public string ApplicantDOB { get; set; }

        [DataMember(Name = "anotherFirstName")]
        public string OnBehalfFirstName { get; set; }

        [DataMember(Name = "anotherMiddleName")]
        public string OnBehalfMiddleName { get; set; }

        [DataMember(Name = "anotherLastName")]
        public string OnBehalfLastName { get; set; }
        
        public AdditionalPersonalInformation(string birthDate, string anotherFirstName, string anotherMiddleName, string anotherLastName)
        {
            ApplicantDOB = birthDate;
            OnBehalfFirstName = anotherFirstName;
            OnBehalfMiddleName = anotherMiddleName;
            OnBehalfLastName = anotherLastName;
        }

    }
    public enum RequestTypes
    {
        Personal,
        General
    }
}
