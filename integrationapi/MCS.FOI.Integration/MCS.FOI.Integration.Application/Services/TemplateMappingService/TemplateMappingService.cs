namespace MCS.FOI.Integration.Application.Services.TemplateService
{
    public class TemplateMappingService : ITemplateMappingService
    {
        private readonly ITemplateDataService _templateDataService;
        private readonly ITemplateFieldMappingRepository _templateFieldMapping;
        private readonly ITemplateListOptionRepository _templateListOptions;

        public TemplateMappingService(
            ITemplateFieldMappingRepository templateFieldMapping,
            ITemplateListOptionRepository templateListOptions,
            ITemplateDataService templateDataService)
        {
            _templateFieldMapping = templateFieldMapping;
            _templateListOptions = templateListOptions;
            _templateDataService = templateDataService;
        }

        public async Task<IEnumerable<TemplateFieldMappingDto>> GenerateFieldsMapping(int foiRequestId, int foiMinistryRequestId)
        {
            var templateFieldMapping = await _templateFieldMapping.GetAsync(r => r.IsActive);
            var templateFieldOptions = await _templateListOptions.GetAsync();

            var mappedFields = IMap.Mapper.Map<IEnumerable<TemplateFieldMappingDto>>(templateFieldMapping);
            var templateFieldDto = mappedFields.Where(r => r.FieldType.Equals("String")).ToList();
            var strFieldMapping = await GenerateStringMapping(foiRequestId, foiMinistryRequestId);

            foreach (var field in templateFieldDto)
            {
                if (strFieldMapping.TryGetValue(field.FieldName.Trim(), out var fieldValue))
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
            var oipc = await _templateDataService.GetFOIRequestOIPC(foiRequestId);
            var programArea = await _templateDataService.GetProgramArea(requestMinistry.ProgramAreaId);
            var applicantCategory = await _templateDataService.GetApplicantCategory(request.ApplicantCategoryId);
            var operatingTeamEmails = await _templateDataService.GetOperatingTeamEmails(requestMinistry.AssignedGroup);
            var extension = await _templateDataService.GetFOIRequestExtensions(foiMinistryRequestId, requestMinistry.Version);

            var applicant = requestApplicants.FirstOrDefault();
            var onBehalf = anotherPerson.FirstOrDefault();
            var primaryOipc = oipc.FirstOrDefault();
            var primaryProgramArea = programArea.FirstOrDefault(r => r.ProgramAreaId == requestMinistry.ProgramAreaId);
            var primaryApplicantCategory = applicantCategory.FirstOrDefault(r => r.ApplicantCategoryId == request.ApplicantCategoryId);
            var extensionData = extension?.FirstOrDefault();

            string? GetContactInfo(string dataFormat) =>
                requestContactInfo.FirstOrDefault(r => r.DataFormat == dataFormat)?.ContactInformation?.ToString();

            string GetFullAddress()
            {
                var addressParts = new[]
                {
                    GetContactInfo("address"),
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
                { "[OIPCNUMBER]", primaryOipc?.OipcNo },
                { "[TODAYDATE]", DateTime.Now.ToString("MMMM dd, yyyy") },
                { "[RQREMAIL]", GetContactInfo("email") },
                { "[RQRFAX]", "(250) 3879843" },
                { "[STREET1]", GetContactInfo("address") },
                { "[STREET2]", string.Empty },
                { "[CITY]", GetContactInfo("city") },
                { "[STATE/PROVINCESHORT]", GetContactInfo("province") },
                { "[COUNTRY]", GetContactInfo("country") },
                { "[ZIP/POSTALCODE]", GetContactInfo("postal") },
                { "[ADDRESS]", GetFullAddress().ToString() },
                { "[RFNAME]", applicant?.FirstName },
                { "[RLNAME]", applicant?.LastName },
                { "[ONBEHALFOF]", string.Join(" ", new[] { onBehalf?.FirstName, onBehalf?.MiddleName, onBehalf?.LastName }
                                      .Where(namePart => !string.IsNullOrWhiteSpace(namePart))) },
                { "[MINISTRYOFXX]", primaryProgramArea?.Name },
                { "[ANALYST]", requestMinistry.AssignedTo },
                { "[REQUESTERCATEGORY]", primaryApplicantCategory?.Description?.ToString() },
                { "[RECEIVEDDATE]", request.ReceivedDate.ToString("MMMM dd, yyyy") },
                { "[REQUESTDESCRIPTION]", request.InitialDescription },
                { "[PAYMENTDUEDATE]", requestMinistry.DueDate.ToString("MMMM dd, yyyy") }, // for inquiries
                { "[REQUESTEDDATE]", request.ReceivedDate.ToString("MMMM dd, yyyy") }, // for inquiries
                { "[PERFECTEDDATE]", request.InitialRecordSearchFromDate?.ToString("MMMM dd, yyyy") },
                { "[APPLICATION_FEE_AMOUNT]", string.Empty }, // for inquiries
                { "[OIPCORDERNUMBER]", string.Empty }, // for inquiries
                { "[DUEDATE]", requestMinistry.DueDate.ToString("MMMM dd, yyyy") }, // for inquiries
                { "[ADDITIONALXX]", extensionData?.ApprovedNoOfDays?.ToString() },
                { "[EXTENDED_DUE_DATE]", extensionData?.ExtendedDueDate?.ToString("MMMM dd, yyyy") },
                { "[PRIMARYUSERREMAIL]", operatingTeamEmails?.FirstOrDefault()?.EmailAddress?.ToString() },
                { "[REQUESTOWNER]", $"{assignee?.FirstName} {assignee?.LastName}" }, // for inquiries
                { "[PRIMARYUSERPHONE]", string.Empty }, // for inquiries
                { "[PRIMARYUSERNAME]", $"{assignee?.FirstName} {assignee?.LastName}" }, // for inquiries
                { "[PRIMARYUSERTITLE]", string.Empty }, // for inquiries
                { "[LINKEDREQUESTS]", primaryProgramArea?.Name }, // for inquiries
                { "[REQUESTERNAME]", $"{applicant?.FirstName} {applicant?.LastName}" }, // for inquiries
                { "[COMPANY]", string.Empty } // for inquiries
            };

            await PopulateFeeAndPaymentData(templateData, foiMinistryRequestId, foiRequestId);

            return templateData;
        }

        private async Task PopulateFeeAndPaymentData(Dictionary<string, string?> templateData, int foiMinistryRequestId, int foiRequestId)
        {
            var approvedCfrFee = await _templateDataService.GetApprovedCRFFee(foiMinistryRequestId);

            if (approvedCfrFee?.FeeData != null)
            {
                var feeData = JsonConvert.DeserializeObject<Dictionary<string, object>>(approvedCfrFee.FeeData.ToString());

                decimal actualTotalDue = feeData.ContainsKey("actualtotaldue") ? Convert.ToDecimal(feeData["actualtotaldue"]) : 0;
                decimal estimatedTotalDue = feeData.ContainsKey("estimatedtotaldue") ? Convert.ToDecimal(feeData["estimatedtotaldue"]) : 0;
                decimal amountPaid = feeData.ContainsKey("amountpaid") ? Convert.ToDecimal(feeData["amountpaid"]) : 0;
                decimal feeWaiverAmount = feeData.ContainsKey("feewaiveramount") ? Convert.ToDecimal(feeData["feewaiveramount"]) : 0;

                decimal invoiceAmount = actualTotalDue > 0 ? actualTotalDue : estimatedTotalDue;
                decimal balanceAmount = invoiceAmount - amountPaid + feeWaiverAmount;

                templateData["[BALANCEAMOUNT]"] = balanceAmount.ToString("F2");
                templateData["[INVOICEAMOUNT]"] = invoiceAmount.ToString("F2");
            }

            var payment = await _templateDataService.GetPayment(foiRequestId, foiMinistryRequestId);
            if (payment != null)
            {
                templateData["[PAIDAMOUNT]"] = payment.PaidAmount?.ToString("F2");
                templateData["[PAYMENTRECEIVEDDATE]"] = payment.CreatedAt.ToString();
            }
        }
    }
}
