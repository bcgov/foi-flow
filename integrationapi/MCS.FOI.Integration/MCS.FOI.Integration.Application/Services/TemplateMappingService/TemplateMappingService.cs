namespace MCS.FOI.Integration.Application.Services.TemplateService
{
    public class TemplateMappingService : ITemplateMappingService
    {
        private readonly ITemplateDataService _templateDataService;
        private readonly ITemplateFieldMappingRepository _templateFieldMapping;

        public TemplateMappingService(
            ITemplateFieldMappingRepository templateFieldMapping,
            ITemplateDataService templateDataService)
        {
            _templateFieldMapping = templateFieldMapping;
            _templateDataService = templateDataService;
        }

        public async Task<IEnumerable<TemplateFieldMappingDto>> GenerateFieldsMapping(int foiRequestId, int foiMinistryRequestId)
        {
            var templateFieldMapping = await _templateFieldMapping.GetAsync(r => r.IsActive);

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
            var assignee = await _templateDataService.GetAssignee(foiMinistryRequestId);
            var requestContactInfo = await _templateDataService.GetRequestContactInformation(foiRequestId, request.Version);
            var requestApplicants = await _templateDataService.GetRequestApplicantInfos(foiRequestId, request.Version, RequestorType.Self);
            var anotherPerson = await _templateDataService.GetRequestApplicantInfos(foiRequestId, request.Version, RequestorType.OnBehalfOf);
            var oipcDetails = await _templateDataService.GetFOIRequestOIPC(foiRequestId, request.Version);
            var programArea = await _templateDataService.GetProgramArea(requestMinistry.ProgramAreaId);
            var applicantCategory = await _templateDataService.GetApplicantCategory(request.ApplicantCategoryId);
            var operatingTeamEmails = await _templateDataService.GetOperatingTeamEmails(requestMinistry.AssignedGroup);
            var paymentFees = await _templateDataService.GetPaymentFees(foiRequestId);
            var originalLdd = await _templateDataService.GetRequestOriginalDueDate(foiMinistryRequestId);
            var receivedModes = await _templateDataService.GetReceivedModes(request.ReceivedModeId ?? 0);
            var foiRequestExtension = await _templateDataService.GetExtensions(foiMinistryRequestId, requestMinistry.Version);
            var oipcExtension = GetExtensionDetails(foiRequestExtension, ExtensionType.OIPC);
            var pbExtension = GetExtensionDetails(foiRequestExtension, ExtensionType.PublicBody);

            var applicant = requestApplicants.FirstOrDefault();
            var onBehalf = anotherPerson.FirstOrDefault();
            var primaryProgramArea = programArea.FirstOrDefault(r => r.ProgramAreaId == requestMinistry.ProgramAreaId);
            var primaryApplicantCategory = applicantCategory.FirstOrDefault(r => r.ApplicantCategoryId == request.ApplicantCategoryId);
            var extensionData = foiRequestExtension?.FirstOrDefault();
            var applicationFees = paymentFees?.Where(r => r.FeeCodeId.Equals(1));

            var displayContent = DisplayApplicantConsentSection(foiRequestExtension, applicant);
            var displayPBExtension = DisplayPBExtension(foiRequestExtension ?? new List<FOIRequestExtensionsDto>());
            var displayOIPCExtension = DisplayOIPCExtension(foiRequestExtension ?? new List<FOIRequestExtensionsDto>());
            var getPBExtensionreason = GetMappedValue("pbextensionreason", pbExtension.ExtensionReason);

            string? GetContactInfo(string dataFormat) =>
                requestContactInfo.FirstOrDefault(r => r.DataFormat == dataFormat)?.ContactInformation?.ToString();

            string GetFullAddress()
            {
                var addressParts = new[]
                {
                    GetContactInfo("address"),
                    GetContactInfo("addressSecondary"),
                    GetContactInfo("city"),
                    GetContactInfo("province"),
                    GetContactInfo("country"),
                    GetContactInfo("postal")
                };
                return string.Join(" ", addressParts.Where(part => !string.IsNullOrWhiteSpace(part)));
            }

            var templateData = new Dictionary<string, string?>
            {
                { "[REQUESTNUMBER]", requestMinistry.AxisRequestId },
                { "[OIPCNUMBER]",  ProcessOipcDetails(oipcDetails.ToList()).oipcNumber},
                { "[TODAYDATE]", DateTime.Now.ToString("MMMM dd, yyyy") },
                { "[RQREMAIL]", GetContactInfo("email") },
                { "[RQRFAX]", "(250) 3879843" },
                { "[ADDRESS]", GetFullAddress().ToString() },
                { "[RFNAME]", applicant?.FirstName },
                { "[RLNAME]", applicant?.LastName },
                { "[ONBEHALFOF]", string.Join(" ", new[] { onBehalf?.FirstName, onBehalf?.MiddleName, onBehalf?.LastName }
                                      .Where(namePart => !string.IsNullOrWhiteSpace(namePart))) },
                { "[MINISTRYOFXX]", primaryProgramArea?.Name },
                { "[ASSIGNEE]", $"{assignee?.FirstName} {assignee?.LastName}" },
                { "[REQUESTERCATEGORY]", primaryApplicantCategory?.Description?.ToString() },
                { "[RECEIVEDDATE]", request.ReceivedDate.ToString("MMMM dd, yyyy") },
                { "[REQUESTDESCRIPTION]", request.InitialDescription },
                { "[PERFECTEDDATE]", request.InitialRecordSearchFromDate?.ToString("MMMM dd, yyyy") },
                { "[APPLICATION_FEE_AMOUNT]", applicationFees.Any() ?
                        applicationFees?.Select(r => (r.Quantity * r.Total)).Sum().ToString() : string.Empty },
                { "[OIPCORDERNUMBER]", string.Join(",", ProcessOipcDetails(oipcDetails.ToList()).oipcOrderNumber) },
                { "[DUEDATE]", requestMinistry.DueDate.ToString("MMMM dd, yyyy") },
                { "[ADDITIONALXX]", extensionData?.ApprovedNoOfDays?.ToString() },
                { "[EXTENDED_DUE_DATE]", extensionData?.ExtendedDueDate?.ToString("MMMM dd, yyyy") },
                { "[PRIMARYUSERREMAIL]", string.Empty },
                { "[PRIMARYUSERPHONE]", string.Empty }, //No need to Map for now. But will be mapped later
                { "[PRIMARYUSERTITLE]", string.Empty }, //No need to Map for now. But will be mapped later
                { "[LINKEDREQUESTS]", AssignMinistryNames(requestMinistry.LinkedRequests, programArea)  },
                { "[STREET1]", GetContactInfo("address") },
                { "[STREET2]", GetContactInfo("addressSecondary") },
                { "[CITY]", GetContactInfo("city") },
                { "[STATE/PROVINCESHORT]", GetContactInfo("province") },
                { "[COUNTRY]", GetContactInfo("country") },
                { "[ZIP/POSTALCODE]", GetContactInfo("postal") },
                { "[REQUESTERNAME]", $"{applicant?.FirstName} {applicant?.LastName}" },
                { "[COMPANY]", $"{applicant?.BusinessName}" },
                { "[RESPONSEDATE]", string.Empty }, //No need to Map for now. But will be mapped later
                { "[ASSIGNEEFIRSTNAME]", $"{assignee?.FirstName}" },
                { "[ASSIGNEELASTNAME]", $"{assignee?.LastName}" },
                { "[ASSIGNEDGROUP]", requestMinistry.AssignedGroup },
                { "[ASSIGNEDGROUPEMAILS]", operatingTeamEmails?.First()?.EmailAddress},
                { "[ARCSNUMBER]", request.RequestType.Equals("general") ? "30": "40" },

                { "[OIPCEXTENSIONDUEDAYS]", oipcExtension?.ExtendedDueDays },
                { "[OIPCAPPLICANTCONSENTSECTION]", displayContent },
                { "[OIPCORIGINALRECEIVEDDATE]", request.ReceivedDate.ToString("MMMM dd, yyyy") },
                { "[OIPCORIGINALDUEDATE]", requestMinistry.OriginalLDD?.ToString("MMMM dd, yyyy") ?? originalLdd?.DueDate.ToString("MMMM dd, yyyy") },
                { "[OIPCCURRENTDUEDATE]", requestMinistry?.DueDate.ToString("MMMM dd, yyyy") },
                { "[OIPCEXTENSIONDUEDATES]", oipcExtension?.ExtendedDueDate.ToString()},
               
                { "[PBEXTENSIONSTATUS]", displayPBExtension},
                { "[OIPCEXTENSIONSECTION]", string.Empty }, // can we mapped it on UI?
                { "[OIPCEXTENSIONLIST]", displayOIPCExtension  },
                { "[FINALPACKAGESTATUS]", string.Empty }, // can we mapped it on UI?
                { "[PBEXTENSIONREASON]",  getPBExtensionreason },
                { "[PBEXTENSIONDUEDAYS]", pbExtension.ExtendedDueDays },
                { "[PBEXTENSIONDUEDATE]", pbExtension.ExtendedDueDate },
                { "[ONLINEFORMHTMLFORACKNOWLEDGEMENTLETTER]", RenderOnlineFormHTML(receivedModes?.First()?.Name) }
            };

            await PopulateFeeAndPaymentData(templateData, foiMinistryRequestId, foiRequestId);

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

                templateData["[BALANCEAMOUNT]"] = balancedue.ToString();
                templateData["[INVOICEAMOUNT]"] = totaldue.ToString();
                templateData["[AMOUNTPAID]"] = amountPaid.ToString();
                templateData["[FEEESTIMATESTATUS]"] = string.Empty;
                templateData["[DEPOSITPAID]"] = (amountPaid - paidAmount).ToString();
                templateData["[PAIDAMOUNT]"] = paidAmount.ToString();
                templateData["[PAYMENTRECEIVEDDATE]"] = payment.CreatedAt.ToString();
            }
        }

        private (string oipcNumber, string oipcOrderNumber) ProcessOipcDetails(List<FOIRequestOIPCDto> oipcDetails)
        {
            var oipcNumber = string.Join(",", oipcDetails.Select(o => o.OipcNo));

            var orderNumbers = oipcDetails
                .Select(r =>
                    JsonConvert.DeserializeObject<InquiryAttributes>(r.InquiryAttributes ?? "{}")?.OrderNo)
                .Where(orderno => !string.IsNullOrEmpty(orderno))
                .ToList();

            var oipcOrderNumber = string.Join(",", orderNumbers);

            return (oipcNumber, oipcOrderNumber);
        }

        private string AssignMinistryNames(string linkedRequestsJson, IEnumerable<ProgramAreaDto> programAreas)
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

        private static ExtensionDetails GetExtensionDetails(IEnumerable<FOIRequestExtensionsDto> requestExtensions, string extensionType)
        {
            if (requestExtensions == null || requestExtensions.ToList().Count == 0)
                return new ExtensionDetails();

            var recentExtension = requestExtensions.FirstOrDefault();
            if (recentExtension == null || string.IsNullOrEmpty(recentExtension.ExtensionType))
                return new ExtensionDetails();

            var extension = new ExtensionDetails();

            if (recentExtension.ExtensionType == ExtensionType.PublicBody &&
                recentExtension.ExtensionStatus?.ToString() == "Approved")
            {
                extension.ExtendedDueDays = recentExtension.ExtendedDueDays?.ToString() ?? string.Empty;
                extension.ExtendedDueDate = recentExtension.ExtendedDueDate?.ToString() ?? string.Empty;
                extension.ExtensionReason = recentExtension.ExtensionReason?.ToString() ?? string.Empty;
            }
            else if (recentExtension.ExtensionType == ExtensionType.OIPC)
            {
                extension.ApprovedNoOfDays = recentExtension.ApprovedNoOfDays?.ToString() ?? string.Empty;
                extension.ExtendedDueDate = recentExtension.ExtendedDueDate?.ToString() ?? string.Empty;
                extension.ExtensionReason = recentExtension.ExtensionReason?.ToString() ?? string.Empty;
                extension.CreatedAt = recentExtension.CreatedAt.ToString() ?? string.Empty;
                extension.ExtensionReasonId = recentExtension.ExtensionReasonId.ToString() ?? string.Empty;
                extension.DecisionDate = recentExtension.DecisionDate?.ToString() ?? string.Empty;
                extension.ExtendedDueDays = recentExtension.ExtendedDueDays?.ToString() ?? string.Empty;
            }

            return extension;
        }

        private static string DisplayApplicantConsentSection(IEnumerable<FOIRequestExtensionsDto> requestExtensions, FOIRequestApplicantInfoDto requestDetails)
        {
            if (!requestExtensions.Any()) return string.Empty;

            var recentOIPCExtension = requestExtensions
                .Where(r => r.ExtensionType.Equals(ExtensionType.OIPC) && r.ExtensionStatus.Equals("Approved"))
                .FirstOrDefault();

            if (recentOIPCExtension == null) return string.Empty;

            return recentOIPCExtension.ExtensionReason.Equals("OIPC - Applicant Consent")
                ? GetOIPCApplicantConsent(requestDetails) : GetOIPCOthers(requestDetails);
        }

        private static string GetOIPCApplicantConsent(FOIRequestApplicantInfoDto requestDetails)
        {
            return $@"
                <p><span style='font-size:13px;font-family:""BC Sans"";'>You have the right to ask the Information and Privacy Commissioner to review this decision. &nbsp;I have enclosed information on the review and complaint process.</span></p>
                <p style=""margin:0cm;""><span style='font-size:13px;font-family:""BC Sans"";'>&nbsp;</span><span style='font-size:13px;font-family:""BC Sans"";'>&nbsp;</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>Sincerely,</span></p>
                <p style=""text-align: center;""><span style=""font-size: 13px; "">&nbsp;</span></p>
                <p style=""text-align: center;""><span style=""font-size: 13px; "">&nbsp;</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>{requestDetails.FirstName} {requestDetails.LastName},&nbsp;</span><span style='font-size:13px;font-family:""BC Sans"";'>IAO Position Title</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>Information Access Operations</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>&nbsp;</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>Enclosure</span></p>
                <strong><span style='font-size:13px;font-family:""BC Sans"";'><br>&nbsp;</span></strong>
            ";
        }

        private static string GetOIPCOthers(FOIRequestApplicantInfoDto requestDetails)
        {
            return $@"
                <p><span style='font-size:13px;font-family:""BC Sans"";'>Sincerely,</span></p>
                <p style=""text-align: center;""><span style=""font-size: 13px; "">&nbsp;</span></p>
                <p style=""text-align: center;""><span style=""font-size: 13px; "">&nbsp;</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>{requestDetails.FirstName} {requestDetails.LastName},&nbsp;</span><span style='font-size:13px;font-family:""BC Sans"";'>IAO Position Title</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>Information Access Operations</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>&nbsp;</span></p>
                <p><span style='font-size:13px;font-family:""BC Sans"";'>Enclosure</span></p>
            ";
        }

        private static string DisplayPBExtension(IEnumerable<FOIRequestExtensionsDto> requestExtensions)
        {
            if (requestExtensions != null && requestExtensions.ToList().Count > 0)
            {
                // Filter out only Public Body extensions that are approved
                var pbExtensions = requestExtensions
                    .Where(ext => ext.ExtensionType == "Public Body" && ext.ExtensionStatus == "Approved")
                    .ToList();

                // Check if there are any PB Extensions
                if (pbExtensions.Any())
                {
                    var recentPBExtension = pbExtensions.First(); // Assuming the list is sorted by date with the most recent first

                    // Extract variables for the HTML template
                    string extendedDueDate = ConvertDate(recentPBExtension.ExtendedDueDate.ToString());
                    int extendedDueDays = recentPBExtension.ExtendedDueDays ?? 0;
                    string extensionReason = MapSectionWithExtensionReasonId(recentPBExtension.ExtensionReasonId);
                    string createdAt = ConvertDate(recentPBExtension.CreatedAt.ToString());

                    // Build the HTML template for "Yes" case
                    string htmlTemplate = $@"
                    <p><strong><span style='font-size: 13px;'>Public Body Extension:&nbsp;</span></strong><span style='font-size: 13px;'>Yes</span></p>
                    <p><strong><span style='font-size: 13px;'>Date of time extension:&nbsp;</span></strong><span style='font-size: 13px;'>{extendedDueDate}</span></p>
                    <p><strong><span style='font-size: 13px;'>Number of days extended:&nbsp;</span></strong><span style='font-size: 13px;'>{extendedDueDays}</span></p>
                    <p><strong><span style='font-size: 13px;'>Reason for Extension:section:&nbsp;</span></strong><span style='font-size: 13px;'>{extensionReason}</span></p>
                    <p><strong><span style='font-size: 13px;'>Date applicant was notified:&nbsp;</span></strong><span style='font-size: 13px;'>{createdAt}</span></p>
                    <p><strong><span style='font-size: 13px;'>Applicant complaint about time extension:&nbsp;</span></strong><span style='font-size: 13px;'>No</span></p>
                ";

                    return htmlTemplate;
                }
            }

            // If no PB Extension is found, return the "No" template
            return @"
            <p><strong><span style='font-size: 13px;'>Public Body Extension:&nbsp;</span></strong><span style='font-size: 13px;'>No</span></p>
        ";
        }

        private static string DisplayOIPCExtension(IEnumerable<FOIRequestExtensionsDto> requestExtensions)
        {
            if (requestExtensions != null && requestExtensions.ToList().Count > 0)
            {
                // Filter out only OIPC extensions that are approved
                var filteredOIPCExtensions = requestExtensions
                    .Where(ext => ext.ExtensionType == "OIPC" && ext.ExtensionStatus == "Approved")
                    .ToList();

                // Check if there are any OIPC Extensions
                if (filteredOIPCExtensions.Any())
                {
                    // Map the extensionreasonid values to their corresponding string values
                    var mappedReasons = filteredOIPCExtensions
                        .Select(ext => MapSectionWithExtensionReasonId(ext.ExtensionReasonId))
                        .ToList();

                    // Join the mapped reasons into a comma-separated string
                    return string.Join(", ", mappedReasons);
                }
            }

            // If no OIPC Extension is found, return an empty string
            return string.Empty;
        }

        private static string ConvertDate(string date)
        {
            // Implement date conversion logic
            return string.IsNullOrEmpty(date) ? "" : DateTime.Parse(date).ToString("yyyy-MM-dd");
        }

        private static string MapSectionWithExtensionReasonId(int extensionReasonId)
        {
            switch (extensionReasonId)
            {
                case 1:
                case 6:
                    return "10(1)(d)"; // 10(1)(d) = Public Body - Applicant Consent / OIPC - Applicant Consent
                case 2:
                case 7:
                    return "10(1)(c)"; // 10(1)(c) = Public Body - Consultation / OIPC - Consultation
                case 3:
                case 8:
                    return "10(1)(a)"; // 10(1)(a) = Public Body - Further detail from applicant required / OIPC - Further detail from applicant required
                case 4:
                case 9:
                    return "10(1)(b)"; // 10(1)(b) = Public Body - Large Volume and/or Volume of Search / OIPC - Large Volume and/or Volume of Search
                default:
                    return "";
            }
        }

        public static class MappedDataList
        {
            public static readonly List<KeyValuePair<string, string>> PbExtensionReasons = new List<KeyValuePair<string, string>>
            {
                new KeyValuePair<string, string>("Public Body - Applicant Consent", "Thank you for consenting to an extension"),
                new KeyValuePair<string, string>("Public Body - Consultation", "Your request requires consultation with a third party or other public body"),
                new KeyValuePair<string, string>("Public Body - Further Detail from Applicant Required", "Your request required further detail from you to identify the requested record(s)"),
                new KeyValuePair<string, string>("Public Body - Large Volume and/or Volume of Search", "Your request involves a large volume and/or search for records"),
                new KeyValuePair<string, string>("Public Body - Large Volume and/or Volume of Search and Consultation", "Your request requires consultation with a third party or other public body and involves a large volume and/or search for records")
            };
        }

        public static string GetMappedValue(string property, string propertyKey)
        {
            if (!string.IsNullOrEmpty(propertyKey) && property == "pbextensionreason")
            {
                return MappedDataList.PbExtensionReasons
                    .FirstOrDefault(extension => extension.Key == propertyKey).Value ?? string.Empty;
            }
            return string.Empty;
        }

        public static string RenderOnlineFormHTML(string receivedMode)
        {
            if (receivedMode != "Online Form")
            {
                // Return the HTML content when the request mode is NOT "Online Form".
                return @"<p style=""text-align: center;""><span style=""font-size: 13px; "">&nbsp;</span></p><p><span style='font-size:13px;font-family:""BC Sans"";'>You submitted your request outside of our online process. For future reference, you can submit both personal and general requests at: <a href=""https://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/open-government/open-information/freedom-of-information""><span style=""font-size: 13px; "">https://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/open-government/open-information/freedom-of-information.</span></a>Using the online process is a fast, easy and secure way to submit your Freedom of Information (FOI) request. It also ensures that we receive the information required to open your request. The webpage also includes frequently asked questions, additional information regarding the FOI process, and links to previously completed FOI requests and proactively released government records. </span></p>";
            }
            return string.Empty;
        }
    }
}
