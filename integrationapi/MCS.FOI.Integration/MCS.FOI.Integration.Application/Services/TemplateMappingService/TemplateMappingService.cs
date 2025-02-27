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
            var foiSubjectCodes = await _templateDataService.GetMinistryRequestSubjectCodes(foiMinistryRequestId, requestMinistry.Version);
            var oipcExtension = GetExtensionDetails(foiRequestExtension, ExtensionType.OIPC);
            var pbExtension = GetExtensionDetails(foiRequestExtension, ExtensionType.PublicBody);

            var applicant = requestApplicants.FirstOrDefault();
            var onBehalf = anotherPerson.FirstOrDefault();
            var primaryProgramArea = programArea.FirstOrDefault(r => r.ProgramAreaId == requestMinistry.ProgramAreaId);
            var primaryApplicantCategory = applicantCategory.FirstOrDefault(r => r.ApplicantCategoryId == request.ApplicantCategoryId);
            var extensionData = foiRequestExtension?.FirstOrDefault();
            var subjectCodes = foiSubjectCodes?.FirstOrDefault();
            var applicationFees = paymentFees?.Where(r => r.FeeCodeId.Equals(1));

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
                { "[RMNAME]", applicant?.MiddleName },
                { "[ONBEHALFOF]", string.Join(" ", new[] { onBehalf?.FirstName, onBehalf?.MiddleName, onBehalf?.LastName }
                                      .Where(namePart => !string.IsNullOrWhiteSpace(namePart))) },
                { "[ACTIONOFFICENAME]", primaryProgramArea?.OfficeName },
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
                { "[ASSIGNEDGROUP]", requestMinistry?.AssignedGroup },
                { "[ASSIGNEDGROUPEMAILS]", operatingTeamEmails?.First()?.EmailAddress},
                { "[ARCSNUMBER]", request.RequestType.Equals("general") ? "30": "40" },

                { "[OIPCEXTENSIONDUEDAYS]", oipcExtension?.ExtendedDueDays },
                { "[OIPCORIGINALRECEIVEDDATE]", request?.ReceivedDate.ToString("MMMM dd, yyyy") },
                { "[OIPCORIGINALDUEDATE]", requestMinistry?.OriginalLDD?.ToString("MMMM dd, yyyy") ?? originalLdd?.DueDate.ToString("MMMM dd, yyyy") },
                { "[OIPCCURRENTDUEDATE]", requestMinistry?.DueDate.ToString("MMMM dd, yyyy") },
                { "[OIPCEXTENSIONDUEDATES]", oipcExtension?.ExtendedDueDate.ToString()},
                { "[PBEXTENSIONDUEDAYS]", pbExtension?.ExtendedDueDays },
                { "[PBEXTENSIONDUEDATE]", pbExtension?.ExtendedDueDate.ToString() },
                { "[EXTENSION_APPROVED_DATE]", extensionData?.DecisionDate.ToString() },
                { "[DOB]", applicant?.DOB.ToString() },
                { "[PHONEPRIMARY]", GetContactInfo("phonePrimary") },
                { "[WORKPHONEPRIMARY]", GetContactInfo("workPhonePrimary") },
                { "[SUBJECTCODE]", subjectCodes?.Name.ToString() }
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

                templateData["[BALANCEAMOUNT]"] = balancedue.ToString("F2");
                templateData["[INVOICEAMOUNT]"] = totaldue.ToString("F2");
                templateData["[AMOUNTPAID]"] = amountPaid.ToString("F2");
                templateData["[FEEESTIMATESTATUS]"] = string.Empty;
                templateData["[DEPOSITPAID]"] = (amountPaid - paidAmount).ToString("F2");
                templateData["[PAIDAMOUNT]"] = paidAmount.ToString("F2");

                if (payment != null && payment.PaymentId != 0)
                    templateData["[PAYMENTRECEIVEDDATE]"] = payment.CreatedAt.ToString("MMMM dd, yyyy");
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
    }
}
