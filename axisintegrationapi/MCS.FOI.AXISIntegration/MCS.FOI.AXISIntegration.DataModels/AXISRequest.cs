using System;
using System.Collections.Generic;

namespace MCS.FOI.AXISIntegration.DataModels
{
    public class AXISRequest
    {

        //MORE PROPERTIES TO ADD HERE. TODO

        public string AXISRequestID { get; set; }
        public string RequestDescription { get; set; }
        public string RequestDescriptionFromDate { get; set; }
        public string RequestDescriptionToDate { get; set; }
        public string RequestType { get; set; }
        public string ReceivedDate { get; set; }
        public string ReceivedDateUF { get; set; }
        public string StartDate { get; set; }
        public string DueDate { get; set; }
        public string Category { get; set; }
        public string ReceivedMode { get; set; }
        public string DeliveryMode { get; set; }
        public bool Ispiiredacted { get; set; }
        public string ApplicantFirstName { get; set; }
        public string ApplicantMiddleName { get; set; }
        public string ApplicantLastName { get; set; }
        public string ApplicantDOB { get; set; }
        public string BusinessName { get; set; }
        public string Email { get; set; }
        public string Address { get; set; }
        public string AddressSecondary { get; set; }
        public string City { get; set; }
        public string Province { get; set; }
        public string Country { get; set; }
        public string PostalCode { get; set; }
        public string PhonePrimary { get; set; }
        public string PhoneSecondary { get; set; }
        public string WorkPhonePrimary { get; set; }
        public string WorkPhoneSecondary { get; set; }
        public string OnBehalfFirstName { get; set; }
        public string OnBehalfMiddleName { get; set; }
        public string OnBehalfLastName { get; set; }
        public Ministry SelectedMinistry { get; set; }
        public List<Extension> Extensions { get; set; }

    }
    public enum RequestTypes
    {
        Personal,
        General
    }
}
