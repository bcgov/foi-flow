--DECLARE  @vcVisibleRequestID VARCHAR(MAX)
--SET  @vcVisibleRequestID = 'CFD-2021-12651','CFD-2021-12905'

SELECT 
				(SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = requestTypes.iLabelID and terminology.tiLocaleID = 1) as requestType,
				requests.sdtReceivedDate as requestProcessStart, 
				requests.vcDescription as requestdescription,
				requests.sdtRqtDescFromdate as reqDescriptionFromDate, 
				requests.sdtRqtDescTodate as reqDescriptionToDate,
				(SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = deliveryModes.iLabelID and terminology.tiLocaleID = 1) as deliveryMode, 
				(SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = receivedModes.iLabelID and terminology.tiLocaleID = 1) as receivedMode,				
				requesterTypes.vcDescription as category,
				requests.vcVisibleRequestID as filenumber,
				
				requests.sdtTargetDate as dueDate, 
				requests.sdtOriginalTargetDate as originalDueDate,
				requests.vcRequestStatus,
				requeststatuses.vcRequestStatus as _requeststatus,
				 (SELECT TOP 1 cfr.sdtDueDate FROM tblRequestForDocuments cfr WITH (NOLOCK) 
                INNER JOIN tblProgramOffices programoffice WITH (NOLOCK) ON programoffice.tiProgramOfficeID = cfr.tiProgramOfficeID 
                WHERE requests.iRequestID = cfr.iRequestID 
                AND requests.tiOfficeID = programoffice.tiOfficeID 
                AND office.OFFICE_ID = programoffice.tiOfficeID
                AND cfr.sdtDueDate IS NOT NULL
                ORDER BY cfr.sdtDueDate DESC) as cfrDueDate,
                requests.sdtRequestedDate as receivedDate, 
				requests.sdtRequestedDate as receivedDateUF
                
                FROM
                tblRequests requests WITH (NOLOCK) LEFT OUTER JOIN EC_OFFICE office WITH (NOLOCK) ON requests.tiOfficeID = office.OFFICE_ID
                LEFT OUTER JOIN tblRequesterTypes  requesterTypes WITH (NOLOCK) ON requests.tiRequesterCategoryID = requesterTypes.tiRequesterTypeID
				LEFT OUTER JOIN tblRequestStatuses requeststatuses WITH (NOLOCK) on requests.irequeststatusid = requeststatuses.irequeststatusid
                LEFT OUTER JOIN tblReceivedModes receivedModes WITH (NOLOCK) ON requests.tiReceivedType = receivedModes.tiReceivedModeID 
                LEFT OUTER JOIN tblDeliveryModes deliveryModes WITH (NOLOCK) ON requests.tiDeliveryType = deliveryModes.tiDeliveryModeID

                LEFT OUTER JOIN tblRequestTypes requestTypes WITH (NOLOCK) ON requests.tiRequestTypeID = requestTypes.tiRequestTypeID
                LEFT OUTER JOIN dbo.TBLdocumentreviewlog reviewlog WITH (NOLOCK) ON requests.IREQUESTID = reviewlog.IREQUESTID
             
                WHERE 
                vcVisibleRequestID IN ('CFD-2022-20261', 'CFD-2021-14313','CFD-2021-12866' , 'CFD-2021-12905', 'CFD-2021-12651') AND
				--vcVisibleRequestID IN ('CFD-2019-92736') AND
				office.OFFICE_CODE = 'CFD' 
				
				AND  requests.vcRequestStatus NOT IN ('Closed')
                GROUP BY requests.vcVisibleRequestID,requests.vcRequestStatus,requeststatuses.vcRequestStatus,requests.sdtReceivedDate, requests.sdtTargetDate, requests.sdtOriginalTargetDate, requests.vcDescription,
                requests.sdtRqtDescFromdate, requests.sdtRqtDescTodate, requests.sdtRequestedDate, office.OFFICE_CODE, requesterTypes.vcDescription,
                receivedModes.iLabelID, deliveryModes.iLabelID, 
                requests.iRequestID, 
                requestTypes.iLabelID, requests.vcVisibleRequestID, requests.tiOfficeID, office.OFFICE_ID