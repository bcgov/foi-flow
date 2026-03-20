# Investigation Report: Invalid Request ID Error on Historical Requests

## Overview
This document consolidates the findings from the investigation into the `psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type integer` error that was occurring on the request management API, specifically at the `/foiwatcher/rawrequest/<requestid>` and `/foicomment/rawrequest/<requestid>` endpoints.

The root cause of the issue was a fundamental disconnect between the ID type passed by the frontend (`axisrequestid`, a string) and the ID type expected by the backend database queries (`requestid`, an integer) when viewing historical requests.

---

## 1. Frontend Findings

The frontend (`forms-flow-web`) was inadvertently passing a string ID to endpoints that expected an integer. The sequence of events leading to this is as follows:

1.  **Dashboard Data Grids:** In `forms-flow-web/src/components/FOI/Dashboard/IAO/AdvancedSearch/DataGridAdvancedSearch.js`, when a user clicks on "Historical AXIS Results", the row link is constructed using the `axisrequestid` string (e.g., `CFD-2024-41913`):
    ```javascript
    const historicalRenderCell = (params) => {
      let link = "./historicalrequest/" + params.row.axisrequestid
      // ...
    ```

2.  **React Routing:** In `FOIAuthenticateRouting.jsx`, the routing configuration captures this string and maps it to the `requestId` parameter:
    ```javascript
    <Route path="/foi/historicalrequest/:requestId">
    ```

3.  **Component Mounting:** The `FOIRequest.js` component extracts this parameter using `const { requestId } = useParams();`. It detects that it is a historical request (`isHistoricalRequest = true`) and proceeds to load historical data. However, it also passes this `requestId` string down to its child components, such as `FOIRequestHeader`.

4.  **Erroneous API Calls:** The `<Watcher>` and `<CommentSection>` components are rendered and their respective `useEffect` hooks are triggered. These components blindly use the `requestId` prop to fetch data, resulting in API calls like:
    *   `GET /api/foiwatcher/rawrequest/CFD-2024-41913`
    *   `GET /api/foicomment/rawrequest/CFD-2024-41913`

---

## 2. Backend Findings

The backend (`request-management-api`) was receiving the string ID and passing it directly to the database layer without proper validation or conversion.

1.  **Missing Input Validation:** The endpoints in `foiwatcher.py` and `foicomment.py` extracted the string `<requestid>` from the URL path.
2.  **Database Query Execution:** These string IDs were passed down to service layers (e.g., `watcherservice().getrawrequestwatchers(requestid)`) and ultimately to SQLAlchemy query parameters.
3.  **PostgreSQL Exception:** According to the schema, the `requestid` column in tables like `FOIRawRequests` and `FOIRawRequestWatchers` is defined as an `Integer`. When SQLAlchemy attempted to execute queries using the string parameter (`requestid='CFD-2024-41913'`), the PostgreSQL driver threw a fatal `invalid input syntax for type integer` exception, leading to a 500 Internal Server Error stack trace.

---

## 3. Resolution

To resolve this issue and prevent the application from crashing, robust integer input parsing and validation were added to the affected backend APIs in `request-management-api`:

*   **Files Modified:**
    *   `request_api/resources/foiwatcher.py`
    *   `request_api/resources/foicomment.py`
*   **Fix Applied:** The endpoints were updated to attempt `int()` parsing on the `requestid` and `ministryrequestid` parameters prior to making database calls. 
*   **Error Handling:** If a `ValueError` is encountered (indicating a string like `CFD-2024` was passed), the API catches the exception and gracefully returns a structured error response (e.g., `{"status": 500, "message": "Invalid Request Id"}`) instead of causing a database exception crash.

*(Note: While this prevents the backend crash, the frontend still initiates these unnecessary network requests for historical records. A future frontend optimization could prevent the `<Watcher>` and `<CommentSection>` components from firing API requests when viewing historical AXIS imports).*

---

## Appendix: Historical Request Endpoints Reference

When a user visits `/foi/historicalrequest/:requestId`, the following endpoints are intentionally queried to fetch historical data. Note that these endpoints span across two different backend microservices.

### `historical-search-api` Microservice
This microservice retrieves historical request metadata from the Enterprise Data Warehouse (EDW).

1.  **Request Details:**
    *   `GET /api/foihistoricalrequest/<requestid>`
    *   *Service Call:* `historicalrequestservice().gethistoricalrequest()`
2.  **Description History:**
    *   `GET /api/foihistoricalrequest/descriptionhistory/<requestid>`
    *   *Service Call:* `historicalrequestservice().gethistoricalrequestdescriptionhistory()`
3.  **Extensions:**
    *   `GET /api/foihistoricalrequest/extensions/<requestid>`
    *   *Service Call:* `historicalrequestservice().gethistoricalrequestextensions()`

### `request-management-api` Microservice
This microservice retrieves the actual attached records or documents associated with the historical request.

4.  **Historical Records/Documents:**
    *   `GET /api/foirecord/historical/<axisrequestid>`
    *   *Service Call:* `recordservice().gethistoricaldocuments(axisrequestid)`
