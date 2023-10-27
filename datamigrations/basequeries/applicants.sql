
SELECT email,firstname,lastname,middleName,birthDate,businessName, STRING_AGG(CAST(requestid as nvarchar(max)),', ') as requests FROM  (
SELECT			
				requesters.vcEmailID as email,
				 
                requesters.vcFirstName as firstName,
                requesters.vcLastName as lastName,
                requesters.vcMiddleName as middleName,
                requestorfields.CUSTOMFIELD35 as birthDate,
                requesters.vcCompany as businessName,				
				requests.vcVisibleRequestID as requestid

                FROM
                tblRequests requests WITH (NOLOCK) LEFT OUTER JOIN EC_OFFICE office WITH (NOLOCK) ON requests.tiOfficeID = office.OFFICE_ID

                LEFT OUTER JOIN tblRequesters requesters WITH (NOLOCK) ON requests.iRequesterID = requesters.iRequesterID

                LEFT OUTER JOIN dbo.TBLREQUESTERCUSTOMFIELDS requestorfields WITH (NOLOCK) ON requesters.iRequesterID = requestorfields.IREQUESTERID

                WHERE 
               office.OFFICE_CODE = 'CFD' AND requests.iRequestStatusID NOT IN (  SELECT iRequestStatusID FROM tblRequestStatuses WHERE vcRequestStatus in ('Closed'))

			 ) AS T

			 --WHERE requestid in ('CFD-2021-12651')

			 GROUP BY email,firstname,lastname,middleName,birthDate,businessName


			
				
                