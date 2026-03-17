# AXIS Integration API - Business Documentation

## Overview
The **AXIS Integration API** (`MCS.FOI.AXISIntegrationWebAPI`) serves as a critical middleware component that bridges the modern FOI Flow system with the legacy AXIS database. It provides RESTful endpoints to securely retrieve Freedom of Information (FOI) request details, extensions, and page counts from the AXIS system while enforcing access control based on user assignments in the FOI Flow system.

## Main Features

### 1. Request Search & Retrieval (`GET /api/RequestSearch/{requestNumber}`)
This feature allows the FOI Flow system to retrieve comprehensive details of a specific FOI request stored in the AXIS system.

#### How the Controller Works
This controller relies on the `[Route("api/[controller]/{requestNumber}")]` attribute and retrieves the data securely:

1.  **Routing and Security Setup:**
    *   **Endpoint Path:** The `[Route]` attribute sets the URL structure to `/api/RequestSearch/{requestNumber}`, where `{requestNumber}` is a dynamic identifier passed to the `Get` method.
    *   **CORS:** `[EnableCors(PolicyName = "FOIOrigins")]` ensures only trusted front-end apps can make requests.
    *   **Authentication:** `[Authorize(Policy = "IAOTeam")]` ensures the user is authenticated and has the `IAOTeam` policy.
2.  **The `Get` Method Workflow:**
    *   **Step 1 - Check High-Level Permissions:** Checks if the current user belongs to the `/IAO Restricted Files Manager` group.
    *   **Step 2 - Determine if User is an Assignee/Watcher:** If not a manager, it queries the FOI Flow PostgreSQL database to find assignees/watchers for the request and compares them against the user's claims.
    *   **Step 3 - Fetch Data from AXIS:** Validates the request number and queries the legacy AXIS database to retrieve the payload.
    *   **Step 4 - Enforce Data Access Rules:** 
        *   **Rule A (Unrestricted/Admin):** If the user is an `IAO Restricted Files Manager` OR the request is not restricted, it returns the data.
        *   **Rule B (Restricted):** If the request is restricted, it verifies the user is an Assignee or Watcher. If so, data is returned; otherwise, it returns an HTTP 401 Unauthorized response.
    *   **Step 5 - Error Handling:** Sanitizes inputs to prevent log injection vulnerabilities before logging any errors.

**Key Data Retrieved:**
*   **Request Details:** Request type (Personal/General), category, dates (received, due, original due, CFR due, start), delivery mode, and request description.
*   **Applicant Information:** Name, business name, address, contact information (email, phone numbers), and additional personal information (e.g., DOB, on-behalf-of details).
*   **Extensions:** Any extensions applied to the request, including reason, status, extended days, and approval/denial dates.
*   **Page Counts:** Total request page count and LAN page count.
*   **Linked Requests:** References to other related FOI requests.
*   **Ministries:** The specific ministry associated with the request.

**Access Control & Authorization (Restricted Requests):**
*   If a request is flagged as "Restricted" in the AXIS system, the API enforces strict access control.
*   It checks the current user's JWT token claims against the FOI Flow database (PostgreSQL) to verify if the user is an **Assignee** or a **Watcher** for that specific request (either a raw request or a ministry request).
*   Users with the `/IAO Restricted Files Manager` group claim automatically have access to restricted requests.
*   If the user is not authorized, the API returns an `Unauthorized` response, protecting sensitive PI (Personal Information).

### 2. Request Page Count Batch Retrieval (`POST /api/RequestsPageCount`)
This feature allows the system to fetch the scanned/processed page counts for multiple AXIS requests in a single batch operation.

**Key Capabilities:**
*   Accepts an array of AXIS Request IDs.
*   Validates the specific format of the Request IDs (e.g., `A-123-456`) and performs checks to prevent SQL injection.
*   Queries the AXIS database to sum the total pages from document review logs, redaction layers, and LAN pages for the requested IDs.
*   Returns a dictionary mapping each valid Request ID to its respective `RequestPageCount` and `LANPageCount`.

## How It Works (Architecture & Data Flow)

### 1. Data Access Layer (DAL)
The application utilizes a custom Data Access Layer to interact with two distinct databases:

*   **AXIS Database (Microsoft SQL Server):** Using `System.Data.SqlClient`, the `RequestsDA` class executes complex grouped SQL queries against the legacy AXIS tables (e.g., `tblRequests`, `tblRequesters`, `TBLDOCUMENTS`, `tblRequestExtensions`). This is the primary source of truth for the request payload. **Crucially, the API's interaction with the AXIS Database is strictly READ-ONLY.** All SQL queries executed are `SELECT` statements (utilizing `WITH (NOLOCK)` for performance); the API *never* inserts, updates, or deletes data in the AXIS system. It only fetches the data to display in the new FOI Flow system.

*   **FOI Flow Database (PostgreSQL):** Using `System.Data.Odbc`, the `FOIFlowRequestUsersDA` class queries the FOI Flow tables (e.g., `FOIRawRequests`, `FOIMinistryRequests`, `FOIRequestWatchers`) to determine the active assignees and watchers for a given request. This is entirely used for authorization purposes.

### 2. Cross-Origin Resource Sharing (CORS) & Security
*   The API enforces a specific CORS policy (`FOIOrigins`) to ensure it only accepts requests from trusted FOI Flow frontend environments.
*   Endpoints are protected using `[Authorize]` attributes, requiring valid JWT tokens. The Request Search endpoint specifically requires the `IAOTeam` policy.

### 3. Data Models
The data heavily relies on the `AXISRequest` model, which acts as a Data Transfer Object (DTO). The DAL maps the raw SQL `DataTable` results into this structured C# object, which is then serialized into JSON format (`RequestsHelper.ConvertRequestToJSON`) and returned to the client.

## Summary
The AXIS Integration API is a specialized, secure read-only service. It ensures that the modern FOI Flow application can seamlessly display legacy AXIS request data while rigorously maintaining the confidentiality of restricted requests through dynamic user assignment verification.
