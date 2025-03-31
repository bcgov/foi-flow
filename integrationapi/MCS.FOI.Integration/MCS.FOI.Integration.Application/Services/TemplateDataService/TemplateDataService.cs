namespace MCS.FOI.Integration.Application.Services.TemplateDataService
{
    public class TemplateDataService : ITemplateDataService
    {
        private readonly IDapperRepository _repository;

        public TemplateDataService(IDapperRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<TemplateFieldMappingDto>> GetTemplateFieldMapping()
        {
            const string query = @"SELECT * FROM public.""TemplateFieldMapping"" WHERE isactive = true";
            return (await _repository.QueryAsync<TemplateFieldMappingDto>(query));
        }

        public async Task<IEnumerable<TemplateDto>> GetTemplates(string fileName)
        {
            const string query = @"SELECT * FROM public.""Template"" WHERE isactive = true and filename = @FileName";
            return (await _repository.QueryAsync<TemplateDto>(query, new { FileName = fileName }));
        }

        public async Task UpdateTemplates(IEnumerable<TemplateDto> templates)
        {
            const string updateQuery = @"UPDATE public.""Template"" SET ""EncodedContent"" = @EncodedContent WHERE ""Id"" = @Id";
            await _repository.UpdateAsync(updateQuery, templates);
        }

        public async Task<IEnumerable<TemplateDto>> GetAllTemplates()
        {
            const string query = @"SELECT * FROM public.""Template"" WHERE isactive = true";
            return (await _repository.QueryAsync<TemplateDto>(query));
        }

        public async Task<FOIRequestDto> GetRequest(int foiRequestId)
        {
            const string query = @"SELECT * FROM public.""FOIRequests"" WHERE foirequestid = @FOIRequestId";
            return (await _repository.QueryAsync<FOIRequestDto>(query, new { FOIRequestId = foiRequestId }))
                ?.OrderByDescending(r => r.Version).FirstOrDefault() ?? new FOIRequestDto();
        }

        public async Task<IEnumerable<FOIRawRequestDTO>> GetRawRequest(int foiRequestId)
        {
            const string query = @"SELECT * FROM public.""FOIRawRequests"" WHERE requestid = @FOIRequestId";
            return (await _repository.QueryAsync<FOIRawRequestDTO>(query, new { FOIRequestId = foiRequestId }));
        }

        public async Task<FOIRequestAssigneeDto> GetAssignee(int foiMinistryRequestId)
        {
            const string query = @"
                SELECT fmr.version, assignedto, fa.firstname, fa.lastname, pa.bcgovcode, fmr.programareaid, f.requesttype, fmr.isoipcreview
                FROM public.""FOIMinistryRequests"" fmr 
	                JOIN public.""FOIRequests"" f on fmr.foirequest_id = f.foirequestid and fmr.foirequestversion_id = f.""version"" 
                FULL OUTER JOIN public.""FOIAssignees"" fa ON fa.username = fmr.assignedto
                INNER JOIN public.""ProgramAreas"" pa ON pa.programareaid = fmr.programareaid
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
            const string query = @"SELECT *, REGEXP_REPLACE(name, '^Ministry of ', '', 'i') AS OfficeName FROM public.""ProgramAreas"" WHERE isactive = true AND programareaid = @ProgramAreaId";
            return await _repository.QueryAsync<ProgramAreaDto>(query, new { ProgramAreaId = programAreaId });
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

        public async Task<IEnumerable<FOIRequestOIPCDto>?> GetFOIRequestOIPC(int? ministryRequestId, int versionId)
        {
            const string queryWithVersion = @"
                            SELECT oipc.*, r.name as Reason 
                            FROM public.""FOIRequestOIPC"" oipc
                            JOIN public.""OIPCReasons"" r
	                            ON oipc.reasonid = r.reasonid
                            WHERE foiministryrequest_id = @MinistryRequestId AND foiministryrequestversion_id = @MinistryRequestVersionId";
            return ((await _repository.QueryAsync<FOIRequestOIPCDto>(queryWithVersion, new { MinistryRequestId = ministryRequestId, MinistryRequestVersionId = versionId }))
                 ?? new List<FOIRequestOIPCDto>())?.OrderByDescending(r => r.OipcId);
        }

        public async Task<IEnumerable<OperatingTeamEmailsDto>> GetOperatingTeamEmails(string? operatingTeamName)
        {
            bool emailsTableExists = await TableExistsAsync("OperatingTeamEmails");
            bool teamsTableExists = await TableExistsAsync("OperatingTeams");

            if (!emailsTableExists || !teamsTableExists)
            {
                return new List<OperatingTeamEmailsDto>();
            }

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

        public async Task<IEnumerable<FOIRequestApplicationFeeDto>> GetApplicationFees(int? rawRequestId)
        {
            bool tableExists = await TableExistsAsync("FOIRequestApplicationFees");

            if (!tableExists)
            {
                return new List<FOIRequestApplicationFeeDto>();
            }

            const string query = @"
                SELECT * FROM public.""FOIRequestApplicationFees""
                WHERE rawrequestid = @RawRequestId
                ORDER BY version DESC"
            ;

            var parameters = new { RawRequestId = rawRequestId };

            return await _repository.QueryAsync<FOIRequestApplicationFeeDto>(query, parameters);
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
                ?.OrderBy(r => r.Version)?.FirstOrDefault() ?? new FOIMinistryRequestDto();
        }

        public async Task<IEnumerable<ReceivedModesDto>> GetReceivedModes(int receivedModeId)
        {
            const string query = @"SELECT * FROM public.""ReceivedModes""";
            return await _repository.QueryAsync<ReceivedModesDto>(query) ?? new List<ReceivedModesDto>();
        }

        public async Task<IEnumerable<SubjectCodeDto>> GetMinistryRequestSubjectCodes(int ministryRequestId, int versionId)
        {
            const string query = @"
                SELECT sc.subjectcodeid, sc.name, sc.description
                FROM public.""FOIMinistryRequestSubjectCodes"" fmrsc
                INNER JOIN public.""SubjectCodes"" sc ON fmrsc.subjectcodeid = sc.subjectcodeid
                WHERE fmrsc.foiministryrequestid = @MinistryRequestId 
                  AND fmrsc.foiministryrequestversion = @MinistryRequestVersionId";

            var parameters = new { MinistryRequestId = ministryRequestId, MinistryRequestVersionId = versionId };

            return await _repository.QueryAsync<SubjectCodeDto>(query, parameters) ?? new List<SubjectCodeDto>();
        }

        public async Task<IEnumerable<FOIRequestPersonalAttributeDto>> GetRequestPersonalAttributes(int foiRequestId, int version)
        {
            const string query = @"
                SELECT foipa.*, pa.name as AttributeName
                FROM public.""FOIRequestPersonalAttributes"" foipa
                JOIN public.""PersonalInformationAttributes"" pa
                ON foipa.personalattributeid = pa.attributeid
                WHERE foirequest_id = @FOIRequestId and foirequestversion_id = @MinistryRequestVersionId;";

            var parameters = new { FOIRequestId = foiRequestId, MinistryRequestVersionId = version };

            return await _repository.QueryAsync<FOIRequestPersonalAttributeDto>(query, parameters);
        }

        public async Task<IEnumerable<FOIOpenInformationRequestsDto>> GetOpenInformationRequests(int ministryRequestId, int versionId)
        {
            bool openInformationTableExists = await TableExistsAsync("FOIOpenInformationRequests");
            bool openInfoPublicationTableExists = await TableExistsAsync("OpenInfoPublicationStatuses");

            if (!openInformationTableExists || !openInfoPublicationTableExists)
            {
                return new List<FOIOpenInformationRequestsDto>();
            }

            const string query = @"
                SELECT oir.*, ps.name as PublicationStatus
                FROM public.""FOIOpenInformationRequests"" oir
                JOIN public.""OpenInfoPublicationStatuses"" ps 
                ON ps.oipublicationstatusid = oir.oipublicationstatus_id
                WHERE foiministryrequest_id = @MinistryRequestId and foiministryrequestversion_id = @MinistryRequestVersionId;";

            var parameters = new { MinistryRequestId = ministryRequestId, MinistryRequestVersionId = versionId };

            return (await _repository.QueryAsync<FOIOpenInformationRequestsDto>(query, parameters))
                ?.OrderByDescending(r => r.FoiOpenInfoRequestId).ToList() ?? new List<FOIOpenInformationRequestsDto>();
        }

        public async Task<IEnumerable<FOIOpenInformationRequestsDto>> GetOpenInformationExemptions(int ministryRequestId, int versionId)
        {
            bool openInfoTableExists = await TableExistsAsync("FOIOpenInformationRequests");
            bool openInfoExemptionsTableExists = await TableExistsAsync("OpenInformationExemptions");

            if (!openInfoTableExists || !openInfoExemptionsTableExists)
            {
                return new List<FOIOpenInformationRequestsDto>();
            }

            const string query = @"
                SELECT oir.*, ps.name as ExemptionName
                FROM public.""FOIOpenInformationRequests"" oir
                JOIN public.""OpenInformationExemptions"" ps
                ON ps.oiexemptionid = oir.oiexemption_id
                WHERE foiministryrequest_id = @MinistryRequestId and foiministryrequestversion_id = @MinistryRequestVersionId;";

            var parameters = new { MinistryRequestId = ministryRequestId, MinistryRequestVersionId = versionId };

            return (await _repository.QueryAsync<FOIOpenInformationRequestsDto>(query, parameters))
                ?.OrderByDescending(r => r.FoiOpenInfoRequestId).ToList() ?? new List<FOIOpenInformationRequestsDto>();
        }

        public async Task<bool> TableExistsAsync(string tableName)
        {
            const string query = @"
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = @TableName
                )";

            var parameters = new { TableName = tableName };
            return await _repository.QuerySingleAsync<bool>(query, parameters);
        }
    }
}
