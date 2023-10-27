

SELECT 
				requests.vcVisibleRequestID as filenumber,
				requests.vcDescription as requestdescription,
				convert(varchar,requests.sdtRqtDescFromdate,120) as reqDescriptionFromDate, 
				convert(varchar,requests.sdtRqtDescTodate,120) as reqDescriptionToDate,
				convert(varchar, requests.sdtReceivedDate,120) as requestProcessStart, 
				convert(varchar,requests.sdtTargetDate,120) as dueDate,
				convert(varchar, (SELECT TOP 1 cfr.sdtDueDate FROM tblRequestForDocuments cfr WITH (NOLOCK) 
                INNER JOIN tblProgramOffices programoffice WITH (NOLOCK) ON programoffice.tiProgramOfficeID = cfr.tiProgramOfficeID 
                WHERE requests.iRequestID = cfr.iRequestID 
                AND requests.tiOfficeID = programoffice.tiOfficeID 
                AND office.OFFICE_ID = programoffice.tiOfficeID
                AND cfr.sdtDueDate IS NOT NULL
                ORDER BY cfr.sdtDueDate DESC),120) as cfrDueDate,								 
                convert(varchar,sum(distinct case when requests.IREQUESTID = reviewlog.IREQUESTID and reviewlog.IDOCID = documents.IDOCID then documents.SIPAGECOUNT 
                when requests.IREQUESTID = redaction.IREQUESTID and redaction.IDOCID = ldocuments.IDOCID then ldocuments.SIPAGECOUNT 
                else 0 end),120) as requestPageCount																	                
                FROM
                tblRequests requests WITH (NOLOCK) LEFT OUTER JOIN EC_OFFICE office WITH (NOLOCK) ON requests.tiOfficeID = office.OFFICE_ID               
				LEFT OUTER JOIN tblRequestStatuses requeststatuses WITH (NOLOCK) on requests.irequeststatusid = requeststatuses.irequeststatusid              
				 LEFT OUTER JOIN dbo.TBLdocumentreviewlog reviewlog WITH (NOLOCK) ON requests.IREQUESTID = reviewlog.IREQUESTID
                
                LEFT OUTER JOIN dbo.TBLRedactionlayers redaction WITH (NOLOCK) ON requests.IREQUESTID = redaction.IREQUESTID
				LEFT OUTER JOIN dbo.TBLDOCUMENTS documents WITH (NOLOCK) ON reviewlog.IDOCID = documents.IDOCID
				 LEFT OUTER JOIN dbo.TBLDOCUMENTS ldocuments WITH (NOLOCK) ON redaction.IDOCID = ldocuments.IDOCID
                WHERE 
                vcVisibleRequestID IN ('CFD-2022-20261', 'CFD-2021-14313','CFD-2021-12866' , 'CFD-2021-12905', 'CFD-2021-12651') AND
				
				office.OFFICE_CODE = 'CFD' 
				
				AND  requests.vcRequestStatus NOT IN ('Closed')
                GROUP BY requests.vcVisibleRequestID,requests.vcRequestStatus,requeststatuses.vcRequestStatus,requests.sdtReceivedDate, requests.sdtTargetDate, requests.sdtOriginalTargetDate, requests.vcDescription,
                requests.sdtRqtDescFromdate, requests.sdtRqtDescTodate, requests.sdtRequestedDate, office.OFFICE_CODE, 
              
                requests.iRequestID, 
               requests.vcVisibleRequestID, requests.tiOfficeID, office.OFFICE_ID