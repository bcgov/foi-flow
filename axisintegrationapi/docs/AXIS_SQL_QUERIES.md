# AXIS Integration API - SQL Queries

This document contains the SQL queries used by the `RequestsDA.cs` Data Access Layer to retrieve Freedom of Information (FOI) request data from the legacy MSSQL AXIS database.

These queries are strictly read-only (`SELECT`) and use `WITH (NOLOCK)` to avoid placing read locks on the legacy system.

## 1. Get Axis Request Data
This is the primary parameterized query used to fetch the comprehensive details of a specific request, including applicant information, request description, dates, properties, and joining across numerous tables to map terminology lookups.
**Location:** `RequestsDA.GetAxisRequestData()`

```sql
SELECT requests.sdtReceivedDate as requestProcessStart, requests.sdtTargetDate as dueDate, requests.sdtOriginalTargetDate as originalDueDate,
requests.vcDescription as [description], requests.sdtRqtDescFromdate as reqDescriptionFromDate, requests.sdtRqtDescTodate as reqDescriptionToDate, 
requests.sdtRequestedDate as receivedDate, requests.sdtRequestedDate as receivedDateUF, office.OFFICE_CODE as selectedMinistry, 
requesterTypes.vcDescription as category,
(SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = receivedModes.iLabelID and terminology.tiLocaleID = 1) as receivedMode,
(SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = deliveryModes.iLabelID and terminology.tiLocaleID = 1) as deliveryMode,
(SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = countries.iLabelID and terminology.tiLocaleID = 1) as country,
(SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = states.iLabelID and terminology.tiLocaleID = 1) as province,
requesters.iRequesterID as axisApplicantID, requesters.vcAddress1 as [address], requesters.vcAddress2 as addressSecondary, requesters.vcCity as city, requesters.vcZipCode as postal,
requesters.vcHome as phonePrimary,
requesters.vcMobile as phoneSecondary,
requesters.vcWork1 as workPhonePrimary,
requesters.vcWork2 as workPhoneSecondary,
requesters.vcFirstName as firstName,
requesters.vcLastName as lastName,
requesters.vcMiddleName as middleName,
requestorfields.CUSTOMFIELD35 as birthDate,
requesters.vcCompany as businessName,
requesters.vcEmailID as email,
onbehalf.vcFirstName as onbehalfFirstName,
onbehalf.vcLastName as onbehalfLastName,
onbehalf.vcMiddleName as onbehalfMiddleName,
(SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = requestTypes.iLabelID and terminology.tiLocaleID = 1) as requestType,
sum(case when requests.IREQUESTID = reviewlog.IREQUESTID and reviewlog.IDOCID = documents.IDOCID then documents.SIPAGECOUNT 
when requests.IREQUESTID = redaction.IREQUESTID and redaction.IDOCID = ldocuments.IDOCID then ldocuments.SIPAGECOUNT 
else 0 end) as requestPageCount,
(case when requestfields.CustomField91 > 0 then requestfields.CustomField91 else 0 end ) as lanPageCount,
REPLACE(requestfields.CUSTOMFIELD33, CHAR(160), ' ') as subjectCode,
requestfields.CUSTOMFIELD75 as identityVerified,
(SELECT TOP 1 cfr.sdtDueDate FROM tblRequestForDocuments cfr WITH (NOLOCK) 
INNER JOIN tblProgramOffices programoffice WITH (NOLOCK) ON programoffice.tiProgramOfficeID = cfr.tiProgramOfficeID 
WHERE requests.iRequestID = cfr.iRequestID 
AND requests.tiOfficeID = programoffice.tiOfficeID 
AND office.OFFICE_ID = programoffice.tiOfficeID
AND cfr.sdtDueDate IS NOT NULL
ORDER BY cfr.sdtDueDate DESC) as cfrDueDate
FROM
tblRequests requests WITH (NOLOCK) LEFT OUTER JOIN EC_OFFICE office WITH (NOLOCK) ON requests.tiOfficeID = office.OFFICE_ID
LEFT OUTER JOIN tblRequesterTypes  requesterTypes WITH (NOLOCK) ON requests.tiRequesterCategoryID = requesterTypes.tiRequesterTypeID
LEFT OUTER JOIN tblReceivedModes receivedModes WITH (NOLOCK) ON requests.tiReceivedType = receivedModes.tiReceivedModeID 
LEFT OUTER JOIN tblDeliveryModes deliveryModes WITH (NOLOCK) ON requests.tiDeliveryType = deliveryModes.tiDeliveryModeID
LEFT OUTER JOIN tblRequesters requesters WITH (NOLOCK) ON requests.iRequesterID = requesters.iRequesterID
LEFT OUTER JOIN tblRequesters onbehalf WITH (NOLOCK) ON requests.iOnBehalfOf = onbehalf.iRequesterID
LEFT OUTER JOIN tblCountries countries WITH (NOLOCK) ON requesters.siCountryID = countries.siCountryID
LEFT OUTER JOIN tblStates states WITH (NOLOCK) ON requesters.siStateID = states.siStateID
LEFT OUTER JOIN tblRequestTypes requestTypes WITH (NOLOCK) ON requests.tiRequestTypeID = requestTypes.tiRequestTypeID
LEFT OUTER JOIN dbo.TBLdocumentreviewlog reviewlog WITH (NOLOCK) ON requests.IREQUESTID = reviewlog.IREQUESTID
LEFT OUTER JOIN dbo.TBLDOCUMENTS documents WITH (NOLOCK) ON reviewlog.IDOCID = documents.IDOCID
LEFT OUTER JOIN dbo.TBLRedactionlayers redaction WITH (NOLOCK) ON requests.IREQUESTID = redaction.IREQUESTID
LEFT OUTER JOIN dbo.TBLDOCUMENTS ldocuments WITH (NOLOCK) ON redaction.IDOCID = ldocuments.IDOCID
LEFT OUTER JOIN dbo.TBLREQUESTERCUSTOMFIELDS requestorfields WITH (NOLOCK) ON requesters.iRequesterID = requestorfields.IREQUESTERID
LEFT OUTER JOIN dbo.TBLREQUESTCUSTOMFIELDS requestfields WITH (NOLOCK) ON requests.iRequestID = requestfields.iRequestID
WHERE 
vcVisibleRequestID = @vcVisibleRequestID
GROUP BY requests.sdtReceivedDate, requests.sdtTargetDate, requests.sdtOriginalTargetDate, requests.vcDescription,
requests.sdtRqtDescFromdate, requests.sdtRqtDescTodate, requests.sdtRequestedDate, office.OFFICE_CODE, requesterTypes.vcDescription,
receivedModes.iLabelID, deliveryModes.iLabelID, countries.iLabelID, states.iLabelID,
requesters.iRequesterID, requesters.vcAddress1, requesters.vcAddress2, requesters.vcCity, requesters.vcZipCode,
requesters.vcHome, requesters.vcMobile, requesters.vcWork1, requesters.vcWork2, requesters.vcFirstName, requesters.vcLastName, requesters.vcMiddleName,
requests.iRequestID, requesters.vcCompany, requesters.vcEmailID, onbehalf.vcFirstName, onbehalf.vcLastName, onbehalf.vcMiddleName,
requestTypes.iLabelID, requests.vcVisibleRequestID, requests.tiOfficeID, office.OFFICE_ID,requestorfields.CUSTOMFIELD35, 
REPLACE(requestfields.CUSTOMFIELD33, CHAR(160), ' '),requestfields.CUSTOMFIELD75, requestfields.CustomField91
```

## 2. Get Axis Extension Data
This parameterized query gets the lifecycle statuses and days for any extensions applied to a specific request.
**Location:** `RequestsDA.GetAxisExtensionData()`

```sql
SELECT loc.vcTerminology AS reason, reqextn.cApprovedStatus AS [status], reqextn.sdtExtendedDate AS extendedduedate, 
reqextn.siExtensionDays AS extensiondays, reqextn.dtApprovedDate AS decisiondate 
FROM tblRequests req WITH (NOLOCK) INNER JOIN tblRequestExtensions reqextn WITH (NOLOCK) ON req.iRequestID = reqextn.iRequestID 
AND req.vcVisibleRequestID = @vcVisibleRequestID
INNER JOIN tblExtensions extn WITH (NOLOCK) ON reqextn.tiExtension = extn.tiExtension 
LEFT OUTER JOIN tblTerminologyLookup loc WITH (NOLOCK) ON loc.iLabelID = extn.iLabelID AND loc.tiLocaleID = 1
```

## 3. Get Axis Linked Requests
This parameterized query formats and aggregates other ministry requests that are legally linked together (e.g. general requests going to multiple ministries).
**Location:** `RequestsDA.GetAxisLinkedRequests()`

```sql
SELECT 
    CONCAT(
        '[',
        STRING_AGG(
            CONCAT('{"', destin_vcVisibleRequestID, '":"', ministry, '"}'),
            ','
        ),
        ']'
    ) AS linkedRequests
FROM(
    SELECT DISTINCT
        destin.vcVisibleRequestID AS destin_vcVisibleRequestID,
        office.OFFICE_CODE AS ministry
    FROM tblRequests origin
    JOIN tblRequestLinks link ON(origin.IREQUESTID = link.iRequestIDOrigin OR origin.IREQUESTID = link.iRequestIDDestin)
    JOIN tblRequests destin ON(link.iRequestIDOrigin = destin.IREQUESTID OR link.iRequestIDDestin = destin.IREQUESTID)
    JOIN EC_OFFICE office ON destin.tiOfficeID = office.OFFICE_ID
    WHERE origin.vcVisibleRequestID = @vcVisibleRequestID
        AND destin.vcVisibleRequestID != @vcVisibleRequestID
) AS destination_table
```

## 4. Get Axis Requests Page Count (Batch IN Clause)
This query takes an array of request IDs and efficiently sums their scanned/digital `requestPageCount` from review logs and `lanPageCount` from custom fields.
**Location:** `RequestsDA.GetAxisRequestsPageCount(string[] arrayOfRequestId)`

```sql
Select vcVisibleRequestID as axisRequestId, sum(case when requests.IREQUESTID = reviewlog.IREQUESTID and reviewlog.IDOCID = documents.IDOCID then documents.SIPAGECOUNT 
when requests.IREQUESTID = redaction.IREQUESTID and redaction.IDOCID = ldocuments.IDOCID then ldocuments.SIPAGECOUNT 
else 0 end) as requestPageCount,
(case when requestfields.CustomField91 > 0 then requestfields.CustomField91 else 0 end ) as lanPageCount
FROM
tblRequests requests WITH (NOLOCK)
LEFT OUTER JOIN dbo.TBLdocumentreviewlog reviewlog WITH (NOLOCK) ON requests.IREQUESTID = reviewlog.IREQUESTID
LEFT OUTER JOIN dbo.TBLDOCUMENTS documents WITH (NOLOCK) ON reviewlog.IDOCID = documents.IDOCID
LEFT OUTER JOIN dbo.TBLRedactionlayers redaction WITH (NOLOCK) ON requests.IREQUESTID = redaction.IREQUESTID
LEFT OUTER JOIN dbo.TBLDOCUMENTS ldocuments WITH (NOLOCK) ON redaction.IDOCID = ldocuments.IDOCID
LEFT OUTER JOIN dbo.TBLREQUESTCUSTOMFIELDS requestfields WITH (NOLOCK) ON requests.iRequestID = requestfields.iRequestID
WHERE vcVisibleRequestID IN ({inClauseValues})
GROUP BY vcVisibleRequestID, requestfields.CustomField91
```

## 5. Get Axis Requests Page Count (All)
Same query structure to fetch page counts but retrieves it for every request without a `WHERE IN()` filter.
**Location:** `RequestsDA.GetAxisRequestsPageCount()`

```sql
Select vcVisibleRequestID as axisRequestId, sum(case when requests.IREQUESTID = reviewlog.IREQUESTID and reviewlog.IDOCID = documents.IDOCID then documents.SIPAGECOUNT 
when requests.IREQUESTID = redaction.IREQUESTID and redaction.IDOCID = ldocuments.IDOCID then ldocuments.SIPAGECOUNT 
else 0 end) as requestPageCount,
(case when requestfields.CustomField91 > 0 then requestfields.CustomField91 else 0 end ) as lanPageCount
FROM
tblRequests requests WITH (NOLOCK)
LEFT OUTER JOIN dbo.TBLdocumentreviewlog reviewlog WITH (NOLOCK) ON requests.IREQUESTID = reviewlog.IREQUESTID
LEFT OUTER JOIN dbo.TBLDOCUMENTS documents WITH (NOLOCK) ON reviewlog.IDOCID = documents.IDOCID
LEFT OUTER JOIN dbo.TBLRedactionlayers redaction WITH (NOLOCK) ON requests.IREQUESTID = redaction.IREQUESTID
LEFT OUTER JOIN dbo.TBLDOCUMENTS ldocuments WITH (NOLOCK) ON redaction.IDOCID = ldocuments.IDOCID
LEFT OUTER JOIN dbo.TBLREQUESTCUSTOMFIELDS requestfields WITH (NOLOCK) ON requests.iRequestID = requestfields.iRequestID
GROUP BY vcVisibleRequestID, requestfields.CustomField91
```
