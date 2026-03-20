# Historical Request Flow: Frontend and Backend Integration

This document explains the architecture and data flow for the Historical Request page (`/foi/historicalrequest`) in the FOI Flow application. Accessing this page triggers interactions across the frontend (`forms-flow-web`) and three distinct backend microservices to compile a complete view of a legacy access request.

---

## 1. Frontend Flow: `/foi/historicalrequest/:requestId`

When a user navigates to a historical request in the browser, the frontend orchestrates the data retrieval process.

### A. Routing and Component Mount
*   **Routing:** The React Router in `FOIAuthenticateRouting.jsx` matches the URL pattern `/foi/historicalrequest/:requestId`. 
*   **Parameter passed:** The `:requestId` parameter is extracted. For historical requests, this is typically an `axisrequestid` string (e.g., `CFD-2024-41913`).
*   **Component Mount:** The main `FOIRequest.js` component mounts and sets a boolean flag `isHistoricalRequest` to true based on the URL path.

### B. Triggering API Calls
In its primary `useEffect` hook, `FOIRequest.js` evaluates `isHistoricalRequest`. When true, it dispatches a series of specific Redux actions to fetch data exclusively for historical requests. These dispatches are mapped to the backend endpoints.

---

## 2. Backend Endpoint Mapping (Across 3 Services)

The frontend dispatches call APIs that span three different backend services to assemble the historical data.

### Service 1: `historical-search-api` (Core Metadata)
This microservice is responsible for querying the Enterprise Data Warehouse (EDW) to retrieve the core metadata, history, and extensions of legacy AXIS requests.

**Frontend Action:** `fetchHistoricalRequestDetails(requestId)`
*   **API Called:** `GET /api/foihistoricalrequest/<requestId>`
*   **Backend Handler:** `historical-search-api/request_api/resources/request.py` -> `FOIHistoricalSearch.get()`
*   **Service Layer:** `historicalrequestservice().gethistoricalrequest()`
*   **Purpose:** Retrieves the main details of the request (applicant info, dates, status) from the EDW.

**Frontend Action:** `fetchFOIHistoricalRequestDescriptionList(requestId)`
*   **API Called:** `GET /api/foihistoricalrequest/descriptionhistory/<requestId>`
*   **Backend Handler:** `historical-search-api/request_api/resources/request.py` -> `FOIHistoricalSearch.get()` (Description endpoint)
*   **Service Layer:** `historicalrequestservice().gethistoricalrequestdescriptionhistory()`
*   **Purpose:** Fetches the audit trail of modifications made to the request's description over time.

**Frontend Action:** `fetchHistoricalExtensions(requestId)`
*   **API Called:** `GET /api/foihistoricalrequest/extensions/<requestId>`
*   **Backend Handler:** `historical-search-api/request_api/resources/request.py` -> `FOIHistoricalSearch.get()` (Extensions endpoint)
*   **Service Service:** `historicalrequestservice().gethistoricalrequestextensions()`
*   **Purpose:** Retrieves any extensions applied to the processing deadline of the historical request.

### Service 2: `request-management-api` (Records and Documents)
This microservice manages the actual records, documents, and attachments associated with a request.

**Frontend Action:** `fetchHistoricalRecords(requestId)`
*   **API Called:** `GET /api/foirecord/historical/<requestId>`
*   **Backend Handler:** `request-management-api/request_api/resources/foirecord.py` -> `FOIRequestGetRecord.get()`
*   **Service Layer:** `recordservice().gethistoricaldocuments()`
*   **Purpose:** Retrieves the links or metadata for the actual PDF records/documents attached to the historical request.

### Service 3: Master Data Services (Shared Lookups)
While not exclusively for historical requests, the frontend component also initializes by parallel-fetching numerous lookup tables (Master Data) necessary to populate dropdowns, interpret status codes, and render the UI correctly. This is routed to the general `request-management-api` or a dedicated master data service depending on the deployment configuration.

**Frontend Actions (Examples):** 
*   `fetchFOICategoryList()` -> `GET /api/foiflow/categories`
*   `fetchClosingReasonList()` -> `GET /api/foiflow/closingreasons`
*   `fetchOIPCOutcomes()` -> `GET /api/foiflow/oipcoutcomes`
*   **Purpose:** Caches static lookup values used globally across the application, ensuring that codes returned by the historical EDW queries can be mapped to human-readable labels in the UI.

---

## 3. Database Queries and ORM Executions

The backend services eventually execute the following database queries to retrieve the EDW data and document records.

### A. `historical-search-api` Queries
These queries pull data from the EDW (`ClosedRequestDetailsPost2018`, `factRequestExtensions`, etc.).

**1. Main Historical Request Query (`factRequestDetails.getrequestbyid`)**
```sql
select 
rd.visualrequestfilenumber,
rd.primaryusername,
rt.requesttypename,
rm.receivedmodename,
dm.deliverymodename,
rqt.requestertypename,
r.firstname, r.middlename, r.lastname, r.company, r.email, r.workphone1, r.workphone2, r.mobile, r.home,	
r2.firstname as behalffirstname, r2.middlename as behalfmiddlename, r2.lastname as behalflastname,
rs.requeststatusname,
a.address1, a.address2, a.city, a.state, a.country, a.zipcode,
rd.description, rd.startdate, rd.closeddate, rd.receiveddate, rd.targetdate AS duedate, rd.originaltargetdate AS originalduedate,
rd.subject,
rd.oipcno, rd.reviewtype, rd.reason, rd.status, rd.portfolioofficer,  rof.orderno, rof.inquirydate, rof.outcome, rof.inquirydate is not null as isinquiry
from public."ClosedRequestDetailsPost2018" rd
left join public."dimRequestStatuses" rs on rs.requeststatusid = rd.requeststatusid
left join public."dimRequesters" r on r.requesterid = rd.requesterid
left join public."dimRequesters" r2 on rd.onbehalfofrequesterid = r2.requesterid
LEFT JOIN "dimRequesterTypes" rqt ON rd.applicantcategoryid = rqt.requestertypeid
left join public."dimReceivedModes" rm on rm.receivedmodeid = rd.receivedmodeid
left join public."dimAddress" a on a.addressid = rd.shipaddressid
left join public."dimRequestTypes" rt on rt.requesttypeid = rd.requesttypeid
left join public."dimDeliveryModes" dm on dm.deliverymodeid = rd.deliverymodeid
left join public."factRequestOIPCFields" rof on rof.foirequestid = rd.foirequestid and rof.activeflag = 'Y'
where rd.visualrequestfilenumber = :requestid and rd.activeflag = 'Y'
-- AND rd.requesttypename NOT LIKE '%Restricted%' (Appended if not restricted manager)
```

**2. Description History Query (`factRequestDetails.getdescriptionhistorybyid`)**
```sql
with dbrequestid as (select foirequestid from public."ClosedRequestDetailsPost2018" where visualrequestfilenumber = :requestid)
SELECT 
description,
modifieddate,
createddate,
modifiedbyusername
FROM public."factRequestDetails"
where foirequestid = (select foirequestid from dbrequestid)
and runcycleid in (select max(runcycleid) from public."factRequestDetails"                
    where foirequestid = (select foirequestid from dbrequestid)
    group by description)	
ORDER BY runcycleid DESC
```

**3. Extensions Query (`factRequestExtensions.getextensionsbyrequestid`)**
```sql
SELECT 
    et.extensiontypename,            
    re.extensiondays,    
    re.extendeddate,
    re.approveddate,
    approvedstatus,
    re.createddate
FROM public."factRequestExtensions" re
join public."dimExtensionTypes" et on et.extensiontypeid = re.extensiontypeid
where foirequestid = (select foirequestid from public."ClosedRequestDetailsPost2018" where visualrequestfilenumber = :requestid) 
and re.activeflag = 'Y'
and re.runcycleid in (
select max(runcycleid) from public."factRequestExtensions"
where foirequestid = (select foirequestid from public."ClosedRequestDetailsPost2018" where visualrequestfilenumber = :requestid)
group by requestextid
)
ORDER BY foirequestid DESC, runcycleid DESC, requestextid DESC
```

### B. `request-management-api` Queries
This references the main operational FOI database to retrieve historical document links.

**4. Historical Documents Query (`HistoricalRecords.getdocuments`)**
This is executed via SQLAlchemy ORM rather than raw SQL text:
```python
query = db.session.query(HistoricalRecords)\
    .filter_by(axisrequestid=axisrequestid)\
    .order_by(HistoricalRecords.attributes.desc(), HistoricalRecords.historicalrecordid.asc())\
    .all()
```

---

## 4. Summary of Data Assembly

1.  **User Access:** User visits `/foi/historicalrequest/CFD-2024-41913`.
2.  **Frontend Initialization:** `forms-flow-web` mounts `FOIRequest.js`.
3.  **EDW Data Fetch:** Frontend queries `historical-search-api` for the core details, description history, and extensions using the `CFD-2024-41913` identifier.
4.  **Document Fetch:** Concurrently, it queries `request-management-api` for the associated historical records.
5.  **Master Data Load:** It ensures all lookup mappings (categories, statuses) are fetched.
6.  **UI Render:** The Redux store consolidates these disparate data streams, allowing the React components to render a unified, read-only view of the legacy request.
