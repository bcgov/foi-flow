using MCS.FOI.Integration.Application.Helpers;

namespace MCS.FOI.Integration.Application.Services.TemplateService
{
    public class TemplateMappingService : ITemplateMappingService
    {
        private readonly ITemplateDataService _templateDataService;
        private readonly IConfiguration _configuration;
        private readonly IHttpContextAccessor _httpContextAccessor;

        public TemplateMappingService(
            ITemplateDataService templateDataService,
            IConfiguration configuration,
            IHttpContextAccessor httpContextAccessor)
        {
            _templateDataService = templateDataService;
            _configuration = configuration;
            _httpContextAccessor = httpContextAccessor;
        }

        public async Task<IEnumerable<TemplateFieldMappingDto>> GenerateFieldsMapping(int foiRequestId, int foiMinistryRequestId)
        {
            var templateFieldMapping = await _templateDataService.GetTemplateFieldMapping();

            var mappedFields = IMap.Mapper.Map<IEnumerable<TemplateFieldMappingDto>>(templateFieldMapping);
            var templateFieldDto = mappedFields.Where(r => r.FieldType.Equals("String")).ToList();
            var strFieldMapping = await GenerateStringMapping(foiRequestId, foiMinistryRequestId);

            foreach (var field in templateFieldDto)
            {
                if (strFieldMapping.TryGetValue(field.FieldMapping.Trim(), out var fieldValue))
                {
                    field.FieldValue = fieldValue ?? string.Empty;
                }
            }
            return templateFieldDto;
        }

        private async Task<Dictionary<string, string?>> GenerateStringMapping(int foiRequestId, int foiMinistryRequestId)
        {
            var request = await _templateDataService.GetRequest(foiRequestId);
            var requestMinistry = await _templateDataService.GetRequestByMinistryRequestId(foiMinistryRequestId);
            bool isRawRequest = request.FOIRequestId.Equals(0) && requestMinistry.FOIMinistryRequestId.Equals(0);

            var templateData = new Dictionary<string, string?>();

            if (isRawRequest) 
            {
                var rawRequest = await GetRawRequestDetails(foiRequestId);
                templateData = await PopulateRawRequestData(rawRequest);
            }
            else
            {
                templateData = await PopulateProcessedRequestData(request, requestMinistry);
            }

            return templateData;
        }

        private async Task<Dictionary<string, string?>> PopulateRawRequestData(RequestDto rawRequest)
        {
            var applicationFees = await _templateDataService.GetApplicationFees(rawRequest.RequestId);
            var additionalInfo = rawRequest?.AdditionalPersonalInfo ?? new PersonalInfoDto();
            var applicantFullName = FormatFullName(rawRequest?.FirstName, rawRequest?.LastName);
            var onBehalfFullName = FormatFullName(additionalInfo?.AnotherFirstName, additionalInfo?.AnotherLastName);
            var assigneeFullName = FormatFullName(rawRequest?.AssignedToFirstName, rawRequest?.AssignedToLastName);
            var receivedDate = !string.IsNullOrEmpty(rawRequest?.ReceivedDate) ? DateHelper.FormatDate(rawRequest?.ReceivedDate) : string.Empty;
            var dateOfBirth = !string.IsNullOrEmpty(additionalInfo?.BirthDate) ? DateHelper.FormatDate(additionalInfo?.BirthDate) : string.Empty;
            var dueDate = !string.IsNullOrEmpty(rawRequest?.DueDate) ? DateHelper.FormatDate(rawRequest?.DueDate) : string.Empty;
            var ministryName = rawRequest?.SelectedMinistries?.FirstOrDefault()?.Name ?? string.Empty;
            var officeName = ministryName.StartsWith("Ministry of ", StringComparison.OrdinalIgnoreCase) ? ministryName.Substring(12) : ministryName;
            var faxNumber = _configuration.GetValue<string>("FaxNumber") ?? "(250) 3879843";
            var assigneeEmail = _httpContextAccessor.HttpContext?.User?.FindFirst(ClaimTypes.Email)?.Value ?? string.Empty;
            var startDate = !string.IsNullOrEmpty(rawRequest?.FromDate) ? DateHelper.FormatDate(rawRequest?.FromDate) : string.Empty;
            var endDate = !string.IsNullOrEmpty(rawRequest?.ToDate) ? DateHelper.FormatDate(rawRequest?.ToDate) : string.Empty;

            string GetAddress()
            {
                var addressParts = new[] { applicantFullName, rawRequest?.Address, rawRequest?.AddressSecondary, rawRequest?.City + ' ' + rawRequest?.Province + ' ' + rawRequest?.Postal };
                return string.Join("\n", addressParts.Where(adrs => !string.IsNullOrWhiteSpace(adrs)));
            }

            string FormatFullName(string? firstName, string? lastName) =>
                string.Join(" ", new[] { firstName, lastName }.Where(name => !string.IsNullOrWhiteSpace(name)));

            return new Dictionary<string, string?>
            {
                ["[REQUESTNUMBER]"] = rawRequest?.AxisRequestId,
                ["[TODAYDATE]"] = DateHelper.GetTodayDate(),
                ["[RQREMAIL]"] = "[SELECTEDEMAILSLIST-NONESELECTED]",
                ["[RQRFAX]"] = faxNumber,
                ["[ADDRESS]"] = GetAddress()?.ToString(),
                ["[RFNAME]"] = rawRequest?.FirstName,
                ["[RLNAME]"] = rawRequest?.LastName,
                ["[RMNAME]"] = string.Empty,
                ["[ONBEHALFOF]"] = onBehalfFullName,
                ["[ACTIONOFFICENAME]"] = officeName,
                ["[ASSIGNEE]"] = assigneeFullName,
                ["[REQUESTERCATEGORY]"] = rawRequest?.Category,
                ["[RECEIVEDDATE]"] = receivedDate,
                ["[REQUESTDESCRIPTION]"] = rawRequest?.Description,
                ["[STARTDATE]"] = startDate,
                ["[ENDDATE]"] = endDate,
                ["[PERFECTEDDATE]"] = DateHelper.FormatDate(rawRequest?.FromDate),
                ["[DUEDATE]"] = DateHelper.FormatDate(rawRequest?.DueDate),
                ["[STREET1]"] = rawRequest?.Address,
                ["[CITY]"] = rawRequest?.City,
                ["[STATE/PROVINCESHORT]"] = rawRequest?.Province,
                ["[COUNTRY]"] = rawRequest?.Country,
                ["[ZIP/POSTALCODE]"] = rawRequest?.Postal,
                ["[REQUESTERNAME]"] = applicantFullName,
                ["[COMPANY]"] = rawRequest?.BusinessName,
                ["[ASSIGNEEFIRSTNAME]"] = rawRequest?.AssignedToFirstName,
                ["[ASSIGNEELASTNAME]"] = rawRequest?.AssignedToLastName,
                ["[ASSIGNEDGROUP]"] = rawRequest?.AssignedGroup,
                ["[DOB]"] = dateOfBirth,
                ["[PHONEPRIMARY]"] = rawRequest?.PhonePrimary,
                ["[WORKPHONEPRIMARY]"] = rawRequest?.WorkPhonePrimary,
                ["[SUBJECTCODE]"] = rawRequest?.SubjectCode,
                ["[CORRECTIONNUMBER]"] = rawRequest?.CorrectionalServiceNumber,
                ["[APPLICATION_FEE_AMOUNT]"] = applicationFees?.FirstOrDefault()?.AmountPaid?.ToString("F2") ?? string.Empty,
                ["[PRIMARYUSERREMAIL]"] = assigneeEmail
            };
        }

        private async Task<Dictionary<string, string?>> PopulateProcessedRequestData(FOIRequestDto request, FOIMinistryRequestDto requestMinistry)
        {
            var applicationFees = await _templateDataService.GetApplicationFees(request.FOIRawRequestId);
            var requestContactInfo = await _templateDataService.GetRequestContactInformation(request.FOIRequestId, request.Version);
            var requestApplicants = await _templateDataService.GetRequestApplicantInfos(request.FOIRequestId, request.Version, RequestorType.Self);
            var anotherPerson = await _templateDataService.GetRequestApplicantInfos(request.FOIRequestId, request.Version, RequestorType.OnBehalfOf);
            var foiOIPCDetails = await _templateDataService.GetFOIRequestOIPC(request.FOIRequestId, request.Version);
            var applicantCategory = await _templateDataService.GetApplicantCategory(request.ApplicantCategoryId);
            var receivedModes = await _templateDataService.GetReceivedModes(request.ReceivedModeId ?? 0);
            var foiPersonalAttribute = await _templateDataService.GetRequestPersonalAttributes(request.FOIRequestId, requestMinistry.Version);
            var assignee = await _templateDataService.GetAssignee(requestMinistry.FOIMinistryRequestId);
            var originalLdd = await _templateDataService.GetRequestOriginalDueDate(requestMinistry.FOIMinistryRequestId);
            var foiRequestExtension = await _templateDataService.GetExtensions(requestMinistry.FOIMinistryRequestId, requestMinistry.Version);
            var openInformationRequest = await _templateDataService.GetOpenInformationRequests(requestMinistry.FOIMinistryRequestId, requestMinistry.Version);
            var foiSubjectCodes = await _templateDataService.GetMinistryRequestSubjectCodes(requestMinistry.FOIMinistryRequestId, requestMinistry.Version);
            var programArea = await _templateDataService.GetProgramArea(requestMinistry.ProgramAreaId);
            var operatingTeamEmails = await _templateDataService.GetOperatingTeamEmails(requestMinistry.AssignedGroup);

            var oipcExtension = GetOIPCExtensionDetails(foiRequestExtension);
            var pbExtension = GetPublicBodyExtensionDetails(foiRequestExtension);

            var applicant = requestApplicants.FirstOrDefault();
            var onBehalf = anotherPerson.FirstOrDefault();
            var primaryProgramArea = programArea.FirstOrDefault(r => r.ProgramAreaId == requestMinistry.ProgramAreaId);
            var primaryApplicantCategory = applicantCategory.FirstOrDefault(r => r.ApplicantCategoryId == request.ApplicantCategoryId);
            var extensionData = foiRequestExtension?.FirstOrDefault() ?? new FOIRequestExtensionsDto();
            var subjectCodes = foiSubjectCodes?.FirstOrDefault() ?? new SubjectCodeDto();
            var fee = applicationFees?.FirstOrDefault();
            var oipcDetails = foiOIPCDetails?.FirstOrDefault() ?? new FOIRequestOIPCDto();
            var openInformation = openInformationRequest?.FirstOrDefault();
            var extensionApprovedDate = extensionData.ExtensionType.Equals(ExtensionType.PublicBody.ToString()) ?
               pbExtension?.ExtendedDueDate : oipcExtension?.ExtendedDueDate;
            var faxNumber = _configuration.GetValue<string>("FaxNumber") ?? "(250) 3879843";
            var assigneeEmail = _httpContextAccessor.HttpContext?.User?.FindFirst(ClaimTypes.Email)?.Value ?? string.Empty;


            string? GetPersonalAttribute(string dataFormat) =>
                foiPersonalAttribute.FirstOrDefault(r => r.AttributeName == dataFormat)?.AttributeValue?.ToString();

            string? GetContactInfo(string dataFormat) =>
                requestContactInfo.FirstOrDefault(r => r.DataFormat == dataFormat)?.ContactInformation?.ToString();

            string GetFullAddress()
            {
                var addressParts = new[]
                {
                    string.Join(" ", new[] { applicant?.FirstName, applicant?.MiddleName, applicant?.LastName }.Where(name => !string.IsNullOrWhiteSpace(name))),
                    GetContactInfo("address"),
                    GetContactInfo("addressSecondary"),
                    string.Join(" ", new[] { GetContactInfo("city"), GetContactInfo("province"), GetContactInfo("postal") }.Where(location => !string.IsNullOrWhiteSpace(location)))
                };
                return string.Join("\n", addressParts.Where(part => !string.IsNullOrWhiteSpace(part)));
            }

            var templateData = new Dictionary<string, string?>
            {
                    ["[REQUESTNUMBER]"] = requestMinistry.AxisRequestId,
                    ["[OIPCNUMBER]"] =  ProcessOipcDetails(oipcDetails).oipcNumber,
                    ["[TODAYDATE]"] = DateHelper.GetTodayDate(),
                    ["[RQREMAIL]"] = "[SELECTEDEMAILSLIST-NONESELECTED]",
                    ["[RQRFAX]"] = faxNumber,
                    ["[ADDRESS]"] = GetFullAddress().ToString(),
                    ["[RFNAME]"] = applicant?.FirstName,
                    ["[RLNAME]"] = applicant?.LastName,
                    ["[RMNAME]"] = applicant?.MiddleName,
                    ["[ONBEHALFOF]"] = string.Join(" ", new[] { onBehalf?.FirstName, onBehalf?.MiddleName, onBehalf?.LastName }.Where(namePart => !string.IsNullOrWhiteSpace(namePart))),
                    ["[ACTIONOFFICENAME]"] = primaryProgramArea?.OfficeName,
                    ["[ASSIGNEE]"] = $"{assignee?.FirstName} {assignee?.LastName}",
                    ["[REQUESTERCATEGORY]"] = primaryApplicantCategory?.Description?.ToString(),
                    ["[RECEIVEDDATE]"] = DateHelper.FormatDate(request.ReceivedDate),
                    ["[REQUESTDESCRIPTION]"] = request?.InitialDescription,
                    ["[STARTDATE]"] = DateHelper.FormatDate(request?.InitialRecordSearchFromDate),
                    ["[ENDDATE]"] = DateHelper.FormatDate(request?.InitialRecordSearchToDate),
                    ["[PERFECTEDDATE]"] = DateHelper.FormatDate(request?.InitialRecordSearchFromDate),
                    ["[APPLICATION_FEE_AMOUNT]"] = fee?.AmountPaid?.ToString("F2") ?? string.Empty,
                    ["[OIPCORDERNUMBER]"] = string.Join(",", ProcessOipcDetails(oipcDetails).oipcOrderNumber),
                    ["[DUEDATE]"] = DateHelper.FormatDate(requestMinistry?.DueDate),
                    ["[ADDITIONALXX]"] = extensionData?.ApprovedNoOfDays?.ToString(),
                    ["[EXTENDED_DUE_DATE]"] = DateHelper.FormatDate(extensionData?.ExtendedDueDate),
                    ["[PRIMARYUSERREMAIL]"] = assigneeEmail,
                    ["[PRIMARYUSERPHONE]"] = string.Empty, //No need to Map for now.
                    ["[PRIMARYUSERTITLE]"] = string.Empty, //No need to Map for now.
                    ["[LINKEDREQUESTS]"] = AssignMinistryNames(requestMinistry.LinkedRequests, programArea),
                    ["[STREET1]"] = GetContactInfo("address"),
                    ["[STREET2]"] = GetContactInfo("addressSecondary"),
                    ["[CITY]"] = GetContactInfo("city"),
                    ["[STATE/PROVINCESHORT]"] = GetContactInfo("province"),
                    ["[COUNTRY]"] = GetContactInfo("country"),
                    ["[ZIP/POSTALCODE]"] = GetContactInfo("postal"),
                    ["[REQUESTERNAME]"] = $"{applicant?.FirstName} {applicant?.LastName}",
                    ["[COMPANY]"] = $"{applicant?.BusinessName}",
                    ["[RESPONSEDATE]"] = string.Empty , //No need to Map for now.
                    ["[ASSIGNEEFIRSTNAME]"] = $"{assignee?.FirstName}",
                    ["[ASSIGNEELASTNAME]"] = $"{assignee?.LastName}",
                    ["[ASSIGNEDGROUP]"] = requestMinistry?.AssignedGroup,
                    ["[ASSIGNEDGROUPEMAILS]"] = operatingTeamEmails?.FirstOrDefault()?.EmailAddress,
                    ["[ARCSNUMBER]"] = (request?.RequestType ?? "").Equals("general") ? "40": "30",
                    ["[OIPCEXTENSIONDUEDAYS]"] = oipcExtension?.ExtendedDueDays,
                    ["[OIPCORIGINALRECEIVEDDATE]"] = DateHelper.FormatDate(request?.ReceivedDate),
                    ["[OIPCORIGINALDUEDATE]"] = DateHelper.FormatDate(requestMinistry?.OriginalLDD) ?? DateHelper.FormatDate(originalLdd?.DueDate),
                    ["[OIPCCURRENTDUEDATE]"] = DateHelper.FormatDate(requestMinistry?.DueDate),
                    ["[OIPCEXTENSIONDUEDATES]"] = oipcExtension?.ExtendedDueDate,
                    ["[PBEXTENSIONDUEDAYS]"] = pbExtension?.ExtendedDueDays,
                    ["[PBEXTENSIONDUEDATE]"] = pbExtension?.ExtendedDueDate,
                    ["[EXTENSION_APPROVED_DATE]"] = extensionApprovedDate,
                    ["[DOB]"] = DateHelper.FormatDate(applicant?.DOB),
                    ["[PHONEPRIMARY]"] = GetContactInfo("phonePrimary"),
                    ["[WORKPHONEPRIMARY]"] = GetContactInfo("workPhonePrimary"),
                    ["[SUBJECTCODE]"] = subjectCodes?.Name?.ToString(),
                    ["[OIPCREASON]"] = oipcDetails?.Reason?.ToString(),
                    ["[PUBLICATIONSTATUS]"] = openInformation?.PublicationStatus?.ToString(),
                    ["[OPENINFORELEASE]"] = openInformation?.ExemptionName?.ToString(),
                    ["[CORRECTIONNUMBER]"] = GetPersonalAttribute("BC Correctional Service Number"),
                    ["[REQFORDOCSDUEDATE]"] = DateHelper.FormatDate(requestMinistry?.CFRDueDate)

            };

            await PopulateFeeAndPaymentData(templateData, requestMinistry.FOIMinistryRequestId, request.FOIRequestId);

            return templateData;
        }

        private async Task PopulateFeeAndPaymentData(Dictionary<string, string?> templateData, int foiMinistryRequestId, int foiRequestId)
        {
            var approvedCfrFee = await _templateDataService.GetApprovedCRFFee(foiMinistryRequestId);

            if (approvedCfrFee?.FeeData != null)
            {
                var cfrfee = await _templateDataService.GetCRFFee(foiMinistryRequestId);
                var payment = await _templateDataService.GetPayment(foiRequestId, foiMinistryRequestId);

                var feeData = JsonConvert.DeserializeObject<Dictionary<string, object>>(approvedCfrFee.FeeData.ToString());
                var cfrfeeData = JsonConvert.DeserializeObject<Dictionary<string, object>>(cfrfee.FeeData.ToString());

                decimal actualtotaldue = feeData.ContainsKey("actualtotaldue") ? Convert.ToDecimal(feeData["actualtotaldue"]) : 0;
                decimal estimatedTotalDue = feeData.ContainsKey("estimatedtotaldue") ? Convert.ToDecimal(feeData["estimatedtotaldue"]) : 0;
                decimal amountPaid = cfrfeeData.ContainsKey("amountpaid") ? Convert.ToDecimal(feeData["amountpaid"]) : 0;
                decimal feeWaiverAmount = feeData.ContainsKey("feewaiveramount") ? Convert.ToDecimal(feeData["feewaiveramount"]) : 0;
                decimal totaldue = actualtotaldue > 0 ? actualtotaldue : estimatedTotalDue;
                decimal balancedue = totaldue - amountPaid + feeWaiverAmount;
                decimal paidAmount = Convert.ToDecimal(payment?.PaidAmount ?? 0);

                templateData["[BALANCEAMOUNT]"] = balancedue.ToString("F2");
                templateData["[INVOICEAMOUNT]"] = totaldue.ToString("F2");
                templateData["[AMOUNTPAID]"] = amountPaid.ToString("F2");
                templateData["[FEEESTIMATESTATUS]"] = string.Empty;
                templateData["[DEPOSITPAID]"] = (amountPaid - paidAmount).ToString("F2");
                templateData["[PAIDAMOUNT]"] = paidAmount.ToString("F2");

                if (payment != null && payment.PaymentId != 0)
                    templateData["[PAYMENTRECEIVEDDATE]"] = DateHelper.FormatDate(payment.CreatedAt);
            }
        }

        private async Task<RequestDto> GetRawRequestDetails(int rawRequestId)
        {
            var rawRequest = await _templateDataService.GetRawRequest(rawRequestId);
            var rData = rawRequest?.OrderByDescending(r=> r.Version).FirstOrDefault();
            if (rData.RequestRawData != null)
            {
                string jsonString = rData.RequestRawData;
                RequestDto details = JsonConvert.DeserializeObject<RequestDto>(jsonString);
                details.Version = rData.Version;
                details.RequestId = rawRequestId;

                return details;
            }

            return null;
        }

        private (string oipcNumber, string oipcOrderNumber) ProcessOipcDetails(FOIRequestOIPCDto oipcDetail)
        {
            var oipcNumber = oipcDetail.OipcNo;

            var oipcOrderNumber = JsonConvert.DeserializeObject<InquiryAttributes>(oipcDetail.InquiryAttributes ?? "{}")?.OrderNo ?? string.Empty;

            return (oipcNumber, oipcOrderNumber);
        }

        private string AssignMinistryNames(string linkedRequestsJson, IEnumerable<ProgramAreaDto> programAreas)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(linkedRequestsJson))
                {
                    return string.Empty;
                }

                var linkedRequests = JsonConvert.DeserializeObject<List<string>>(linkedRequestsJson) ?? new List<string>();

                var names = linkedRequests
                    .Select(request => int.TryParse(request, out int programAreaId)
                        ? programAreas.FirstOrDefault(f => f.ProgramAreaId == programAreaId)?.Name
                        : null)
                    .Where(name => name != null)
                    .ToList();

                return string.Join(",", names);
            }
            catch
            {
                return string.Empty; // for update
            }
        }

        private static ExtensionDetails GetPublicBodyExtensionDetails(IEnumerable<FOIRequestExtensionsDto> requestExtensions)
        {
            if (requestExtensions == null || requestExtensions.ToList().Count == 0)
                return new ExtensionDetails();

            var recentExtension = requestExtensions.FirstOrDefault();
            if (recentExtension == null || string.IsNullOrEmpty(recentExtension.ExtensionType))
                return new ExtensionDetails();

            var extension = new ExtensionDetails();

            if (recentExtension.ExtensionType == ExtensionType.PublicBody)
            {
                extension.ExtendedDueDays = recentExtension.ExtendedDueDays?.ToString() ?? string.Empty;
                extension.ExtendedDueDate = DateHelper.FormatDate(recentExtension.ExtendedDueDate) ?? string.Empty;
                extension.ExtensionReason = recentExtension.ExtensionReason?.ToString() ?? string.Empty;
                return extension;
            }

            return extension;
        }

        private static ExtensionDetails GetOIPCExtensionDetails(IEnumerable<FOIRequestExtensionsDto> requestExtensions)
        {
            if (requestExtensions == null || requestExtensions.ToList().Count == 0)
                return new ExtensionDetails();

            var recentExtension = requestExtensions.FirstOrDefault();
            if (recentExtension == null || string.IsNullOrEmpty(recentExtension.ExtensionType))
                return new ExtensionDetails();

            var extension = new ExtensionDetails();

            if (recentExtension.ExtensionType == ExtensionType.OIPC)
            {
                extension.ApprovedNoOfDays = recentExtension.ApprovedNoOfDays?.ToString() ?? string.Empty;
                extension.ExtendedDueDate = DateHelper.FormatDate(recentExtension.ExtendedDueDate) ?? string.Empty;
                extension.ExtensionReason = recentExtension.ExtensionReason?.ToString() ?? string.Empty;
                extension.CreatedAt = DateHelper.FormatDate(recentExtension.CreatedAt) ?? string.Empty;
                extension.ExtensionReasonId = recentExtension.ExtensionReasonId.ToString() ?? string.Empty;
                extension.DecisionDate = DateHelper.FormatDate(recentExtension.DecisionDate) ?? string.Empty;
                extension.ExtendedDueDays = recentExtension.ExtendedDueDays?.ToString() ?? string.Empty;
                return extension;
            }

            return extension;
        }
    }
}
