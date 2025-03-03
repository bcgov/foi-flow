namespace MCS.FOI.Integration.Core.DTOs
{
    public class RequestDto
    {
        public int RequestId { get; set; }
        public string? DueDate { get; set; }
        public string? ReceivedMode { get; set; }
        public string? DeliveryMode { get; set; }
        public string? AxisRequestId { get; set; }
        public string? AssignedGroup { get; set; }
        public string? AssignedTo { get; set; }
        public string? AssignedToFirstName { get; set; }
        public string? AssignedToLastName { get; set; }
        public string? AssignedToName { get; set; }
        public string? FirstName { get; set; }
        public string? LastName { get; set; }
        public string? Email { get; set; }
        public string? Address { get; set; }
        public string? City { get; set; }
        public string? Province { get; set; }
        public string? Country { get; set; }
        public string? Postal { get; set; }
        public string? BusinessName { get; set; }
        public string? Category { get; set; }
        public string? PhonePrimary { get; set; }
        public string? WorkPhonePrimary { get; set; }
        public string? PhoneSecondary { get; set; }
        public string? WorkPhoneSecondary { get; set; }
        public string? AddressSecondary { get; set; }
        public string? FromDate { get; set; }
        public string? ToDate { get; set; }
        public string? Description { get; set; }
        public List<MinistryDto> SelectedMinistries { get; set; }
        public string? SubjectCode { get; set; }
        public string? ReceivedDate { get; set; }
        public string? ReceivedDateUF { get; set; }
        public string? RequestProcessStart { get; set; }
        public string? RequestType { get; set; }
        public PersonalInfoDto AdditionalPersonalInfo { get; set; }
        public string? CorrectionalServiceNumber { get; set; }
        public string? PublicServiceEmployeeNumber { get; set; }
        public string? RequestStatusLabel { get; set; }
        public object UserRecordsLockStatus { get; set; }
    }
    public class MinistryDto
    {
        public string? Code { get; set; }
        public string? Name { get; set; }
        public bool IsSelected { get; set; }
    }

    public class PersonalInfoDto
    {
        public string? AlsoKnownAs { get; set; }
        public string? BirthDate { get; set; }
        public string? ChildFirstName { get; set; }
        public string? ChildMiddleName { get; set; }
        public string? ChildLastName { get; set; }
        public string? ChildAlsoKnownAs { get; set; }
        public string? ChildBirthDate { get; set; }
        public string? AnotherFirstName { get; set; }
        public string? AnotherMiddleName { get; set; }
        public string? AnotherLastName { get; set; }
        public string? AnotherAlsoKnownAs { get; set; }
        public string? AnotherBirthDate { get; set; }
        public string? AdoptiveMotherFirstName { get; set; }
        public string? AdoptiveMotherLastName { get; set; }
        public string? AdoptiveFatherFirstName { get; set; }
        public string? AdoptiveFatherLastName { get; set; }
        public string? PersonalHealthNumber { get; set; }
    }
}
