namespace MCS.FOI.Integration.Application.Services.TemplateDataService
{
    public class TemplateDataService : ITemplateDataService
    {
        private readonly IDapperRepository _repository;

        public TemplateDataService(IDapperRepository repository)
        {
            _repository = repository;
        }


        public async Task<FOIRequestDto> GetRequest(int foiRequestId)
        {
            const string query = @"SELECT * FROM public.""FOIRequests"" WHERE foirequestid = @FOIRequestId";
            return (await _repository.QueryAsync<FOIRequestDto>(query, new { FOIRequestId = foiRequestId }))
                ?.OrderByDescending(r => r.Version).FirstOrDefault() ?? new FOIRequestDto();
        }

        public async Task<FOIRequestAssigneeDto> GetAssignee(int foiMinistryRequestId)
        {
            const string query = @"SELECT fmr.version, assignedto, fa.firstname, fa.lastname, pa.bcgovcode, fmr.programareaid, f.requesttype, fmr.isoipcreview
                FROM public.""FOIMinistryRequests"" fmr 
	                JOIN public.""FOIRequests"" f on fmr.foirequest_id = f.foirequestid and fmr.foirequestversion_id = f.""version"" 
                FULL OUTER JOIN public.""FOIAssignees"" fa ON fa.username = fmr.assignedto
                INNER JOIN ""ProgramAreas"" pa ON pa.programareaid = fmr.programareaid
                WHERE foiministryrequestid = @FOIMinistryRequestid
                ";
            return (await _repository.QueryAsync<FOIRequestAssigneeDto>(query, new { FOIMinistryRequestid = foiMinistryRequestId }))
                ?.OrderByDescending(r => r.Version).FirstOrDefault() ?? new FOIRequestAssigneeDto();
        }

        public async Task<FOIMinistryRequestDto> GetRequestByMinistryRequestId(int foiMinistryRequestId)
        {
            const string query = @"SELECT * FROM public.""FOIMinistryRequests"" WHERE foiministryrequestid = @FOIMinistryRequestid";
            return (await _repository.QueryAsync<FOIMinistryRequestDto>(query, new { FOIMinistryRequestid = foiMinistryRequestId }))
                ?.OrderByDescending(r => r.Version).FirstOrDefault() ?? new FOIMinistryRequestDto();
        }

        public async Task<IEnumerable<FOIRequestContactInformationDto>> GetRequestContactInformation(int foiRequestId, int version)
        {
            const string query = @"SELECT * FROM public.""FOIRequestContactInformation"" WHERE foirequest_id = @FOIRequestId AND foirequestversion_id = @Version";
            return (await _repository.QueryAsync<FOIRequestContactInformationDto>(query, new { FOIRequestId = foiRequestId, Version = version }))
                .OrderBy(r => r.FOIRequestContactId);
        }

        public async Task<IEnumerable<FOIRequestApplicantInfoDto>> GetRequestApplicantInfos(int foiRequestId, int version, RequestorType requestorTypeId)
        {
            const string query = @"
                SELECT 
                    fmap.foirequestapplicantmappingid,
                    fmap.foirequest_id AS foirequestid,
                    fmap.foirequestversion_id AS version,
                    fmap.requestortypeid,
                    rt.name AS requestortype,
                    fa.foirequestapplicantid,
                    fa.firstname,
                    fa.lastname,
                    fa.middlename,
                    fa.alsoknownas,
                    fa.dob,
                    fa.businessname,
                    fa.axisapplicantid
                FROM public.""FOIRequestApplicantMappings"" fmap
                INNER JOIN public.""FOIRequestApplicants"" fa
                    ON fa.foirequestapplicantid = fmap.foirequestapplicantid
                INNER JOIN public.""RequestorTypes"" rt
                    ON rt.requestortypeid = fmap.requestortypeid
                WHERE fmap.foirequest_id = @FOIRequestId 
                  AND fmap.foirequestversion_id = @Version
                  AND fmap.requestortypeid = @RequestorTypeId;
            ";
            return (await _repository.QueryAsync<FOIRequestApplicantInfoDto>(query, new { FOIRequestId = foiRequestId, Version = version, RequestorTypeId = requestorTypeId }))
                .OrderBy(r => r.FOIRequestApplicantMappingId);
        }

        public async Task<IEnumerable<ProgramAreaDto>> GetProgramArea(int? programAreaId)
        {
            const string query = @"SELECT * FROM public.""ProgramAreas"" WHERE isactive = true AND programareaid = @ProgramAreaId";
            return await _repository.QueryAsync<ProgramAreaDto>(query, new { ProgramAreaId = programAreaId });
        }

        public async Task<IEnumerable<ProgramAreaDto>> GetProgramAreas()
        {
            const string query = @"SELECT * FROM public.""ProgramAreas"" WHERE isactive = true";
            return await _repository.QueryAsync<ProgramAreaDto>(query);
        }

        public async Task<IEnumerable<ApplicantCategoryDto>> GetApplicantCategory(int? applicantCategoryId)
        {
            const string query = @"SELECT * FROM public.""ApplicantCategories"" WHERE isactive = true AND applicantcategoryid = @ApplicantCategoryId";
            return await _repository.QueryAsync<ApplicantCategoryDto>(query, new { ApplicantCategoryId = applicantCategoryId });
        }

        public async Task<FOIRequestCFRFeesDto> GetApprovedCRFFee(int? ministryRequestId)
        {
            const string query = @"SELECT * FROM public.""FOIRequestCFRFees"" WHERE cfrfeestatusid = 2 AND ministryrequestid = @MinistryRequestId";
            return (await _repository.QueryAsync<FOIRequestCFRFeesDto>(query, new { MinistryRequestId = ministryRequestId }))
                ?.OrderByDescending(r => r.CFRFeeId).ThenByDescending(r => r.Version).FirstOrDefault() ?? new FOIRequestCFRFeesDto();
        }

        public async Task<FOIRequestCFRFeesDto> GetCRFFee(int? ministryRequestId)
        {
            const string query = @"SELECT * FROM public.""FOIRequestCFRFees"" WHERE ministryrequestid = @MinistryRequestId";
            return (await _repository.QueryAsync<FOIRequestCFRFeesDto>(query, new { MinistryRequestId = ministryRequestId }))
                ?.OrderByDescending(r => r.CFRFeeId).ThenByDescending(r => r.Version).FirstOrDefault() ?? new FOIRequestCFRFeesDto();
        }

        public async Task<FOIRequestPaymentDto> GetPayment(int? foiRequestId, int? ministryRequestId)
        {
            const string query = @"SELECT * FROM public.""FOIRequestPayments"" WHERE foirequestid = @FOIRequestId AND ministryrequestid = @MinistryRequestId";
            return (await _repository.QueryAsync<FOIRequestPaymentDto>(query, new { FOIRequestId = foiRequestId, MinistryRequestId = ministryRequestId }))
                ?.OrderByDescending(r => r.PaymentId).FirstOrDefault() ?? new FOIRequestPaymentDto();
        }

        public async Task<IEnumerable<FOIRequestOIPCDto>> GetFOIRequestOIPC(int? ministryRequestId, int versionId)
        {
            const string queryWithVersion = @"SELECT * FROM public.""FOIRequestOIPC"" WHERE foiministryrequest_id = @MinistryRequestId AND foiministryrequestversion_id = @MinistryRequestVersionId";
            return (await _repository.QueryAsync<FOIRequestOIPCDto>(queryWithVersion, new { MinistryRequestId = ministryRequestId, MinistryRequestVersionId = versionId }))
                ?.OrderBy(r => r.OipcId) ?? Enumerable.Empty<FOIRequestOIPCDto>();
        }

        public async Task<IEnumerable<OperatingTeamEmailsDto>> GetOperatingTeamEmails(string? operatingTeamName)
        {
            const string query = @"
                SELECT email_address as EmailAddress FROM public.""OperatingTeamEmails"" em
                JOIN public.""OperatingTeams"" op
                ON em.teamid = op.teamid
                WHERE em.isactive = true AND op.name = @OperatingTeamName
                ORDER BY emailid ASC"
            ;

            var parameters = new { OperatingTeamName = operatingTeamName };

            return await _repository.QueryAsync<OperatingTeamEmailsDto>(query, parameters);
        }

        public async Task<IEnumerable<FOIRequestExtensionsDto>> GetFOIRequestExtensions(int? ministryRequestId, int? ministryRequestVersionId)
        {
            const string query = @"
                SELECT * 
                FROM public.""FOIRequestExtensions"" 
                WHERE isactive = true and foiministryrequest_id = @MinistryRequestId AND foiministryrequestversion_id = @MinistryRequestVersionId"
            ;

            var parameters = new { MinistryRequestId = ministryRequestId, MinistryRequestVersionId = ministryRequestVersionId };

            return await _repository.QueryAsync<FOIRequestExtensionsDto>(query, parameters);
        }

        public async Task<IEnumerable<PaymentDto>> GetPaymentFees(int foiRequestId)
        {
            const string query = @"
                SELECT * 
                FROM public.""Payments"" 
                WHERE request_id = @FOIRequestId"
            ;

            var parameters = new { FOIRequestId = foiRequestId };

            return await _repository.QueryAsync<PaymentDto>(query, parameters);
        }

        public async Task<IEnumerable<FOIRequestExtensionsDto>> GetExtensions(int? ministryRequestId, int? ministryRequestVersionId)
        {
            const string query = @"
                    SELECT * FROM (
	                      SELECT DISTINCT ON (foirequestextensionid) 
		                    foirequestextensionid, 
		                    fre.extensionreasonid, 
		                    er.reason as ExtensionReason,
		                    er.extensiontype,
		                    fre.extensionstatusid, 
		                    es.name as ExtensionStatus,
		                    extendedduedays, 
		                    extendedduedate, 
		                    decisiondate, 
		                    approvednoofdays, 
		                    fre.isactive, 
		                    created_at as CreatedAt, 
		                    createdby, 
		                    fre.version 
	                     FROM ""public"".""FOIRequestExtensions"" fre 
		                 INNER JOIN ""public"".""ExtensionReasons"" er ON fre.extensionreasonid = er.extensionreasonid 
		                 INNER JOIN ""public"".""ExtensionStatuses"" es ON fre.extensionstatusid = es.extensionstatusid 
	                     WHERE foiministryrequest_id = @MinistryRequestId and foiministryrequestversion_id = @MinistryRequestVersionId 
	                     ORDER BY foirequestextensionid, version DESC) 
                    AS list 
                    ORDER BY extensionstatusid ASC, CreatedAt DESC
               "
            ;

            var parameters = new { MinistryRequestId = ministryRequestId, MinistryRequestVersionId = ministryRequestVersionId };

            return await _repository.QueryAsync<FOIRequestExtensionsDto>(query, parameters);
        }

        public async Task<FOIMinistryRequestDto> GetRequestOriginalDueDate(int ministryRequestId)
        {
            const string query = @"SELECT * FROM public.""FOIMinistryRequests"" 
                WHERE foiministryrequestid = @MinistryRequestId AND requeststatuslabel = 'open'";

            var parameters = new { MinistryRequestId = ministryRequestId };

            return (await _repository.QueryAsync<FOIMinistryRequestDto>(query, parameters))
                ?.OrderBy(r => r.Version)?.First() ?? new FOIMinistryRequestDto();
        }

        public async Task<IEnumerable<ReceivedModesDto>> GetReceivedModes(int receivedModeId)
        {
            const string query = @"SELECT * FROM public.""ReceivedModes""";
            return await _repository.QueryAsync<ReceivedModesDto>(query) ?? new List<ReceivedModesDto>();
        }
    }
}
