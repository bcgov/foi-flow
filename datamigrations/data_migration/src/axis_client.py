from __future__ import annotations

import logging


LOGGER = logging.getLogger(__name__)


PARENT_REQUEST_QUERY = """
SELECT
    (SELECT terminology.vcTerminology
     FROM tblTerminologyLookup terminology
     WHERE terminology.iLabelID = requestTypes.iLabelID
       AND terminology.tiLocaleID = 1) AS requestType,
    CONVERT(varchar, requests.sdtRequestedDate, 120) AS receivedDate,
    requests.vcDescription AS requestdescription,
    CONVERT(varchar, ISNULL(requests.sdtRqtDescFromdate, ''), 120) AS reqDescriptionFromDate,
    CONVERT(varchar, ISNULL(requests.sdtRqtDescTodate, ''), 120) AS reqDescriptionToDate,
    ISNULL((SELECT REPLACE(terminology.vcTerminology, '-', '')
            FROM tblTerminologyLookup terminology
            WHERE terminology.iLabelID = receivedModes.iLabelID
              AND terminology.tiLocaleID = 1), 'Email') AS receivedMode,
    requesterTypes.vcDescription AS category,
    requests.vcVisibleRequestID AS filenumber
FROM tblRequests requests WITH (NOLOCK)
LEFT OUTER JOIN EC_OFFICE office WITH (NOLOCK) ON requests.tiOfficeID = office.OFFICE_ID
LEFT OUTER JOIN tblRequesterTypes requesterTypes WITH (NOLOCK) ON requests.tiRequesterCategoryID = requesterTypes.tiRequesterTypeID
LEFT OUTER JOIN tblReceivedModes receivedModes WITH (NOLOCK) ON requests.tiReceivedType = receivedModes.tiReceivedModeID
LEFT OUTER JOIN tblRequestTypes requestTypes WITH (NOLOCK) ON requests.tiRequestTypeID = requestTypes.tiRequestTypeID
WHERE requests.vcVisibleRequestID = ?
  AND office.OFFICE_CODE = ?
"""


MINISTRY_REQUEST_QUERY = """
SELECT
  requests.vcVisibleRequestID AS filenumber,
  requests.vcDescription AS requestdescription,
  CONVERT(varchar, ISNULL(requests.sdtRqtDescFromdate, ''), 120) AS reqDescriptionFromDate,
  CONVERT(varchar, ISNULL(requests.sdtRqtDescTodate, ''), 120) AS reqDescriptionToDate,
  CONVERT(varchar, requests.sdtReceivedDate, 120) AS requestProcessStart,
  CONVERT(varchar, requests.sdtTargetDate, 120) AS dueDate,
  CONVERT(varchar, requests.sdtOriginalTargetDate, 120) AS originalDueDate,
  '' AS cfrDueDate,
  '0' AS requestPageCount,
  '[]' AS linkedRequests,
  'null' AS identityVerified
FROM tblRequests requests WITH (NOLOCK)
LEFT OUTER JOIN EC_OFFICE office WITH (NOLOCK) ON requests.tiOfficeID = office.OFFICE_ID
WHERE requests.vcVisibleRequestID = ?
  AND office.OFFICE_CODE = ?
"""


APPLICANTS_QUERY = """
SELECT
    requesters.vcFirstName AS firstName,
    requesters.vcLastName AS lastName,
    requesters.vcMiddleName AS middleName,
    requestorfields.CUSTOMFIELD35 AS birthDate,
    requesters.vcCompany AS businessName,
    requests.vcVisibleRequestID AS requestid,
    1 AS MainApplicant
FROM tblRequests requests WITH (NOLOCK)
LEFT OUTER JOIN EC_OFFICE office WITH (NOLOCK) ON requests.tiOfficeID = office.OFFICE_ID
LEFT OUTER JOIN tblRequesters requesters WITH (NOLOCK) ON requests.iRequesterID = requesters.iRequesterID
LEFT OUTER JOIN dbo.TBLREQUESTERCUSTOMFIELDS requestorfields WITH (NOLOCK) ON requesters.iRequesterID = requestorfields.IREQUESTERID
WHERE requests.vcVisibleRequestID = ?
  AND office.OFFICE_CODE = ?
"""


CONTACT_INFORMATION_QUERY = """
SELECT
    ISNULL(requesters.vcEmailID, '') AS email,
    ISNULL(requesters.vcAddress1, '') AS address1,
    ISNULL(requesters.vcAddress2, '') AS address2,
    ISNULL(requesters.vcCity, '') AS city,
    ISNULL(requesters.vcZipCode, '') AS zipcode,
    ISNULL(requesters.vcWork1, '') AS work1,
    ISNULL(requesters.vcWork2, '') AS work2,
    ISNULL(requesters.vcMobile, '') AS mobile,
    ISNULL(requesters.vcHome, '') AS home,
    '' AS country,
    '' AS province,
    requests.vcVisibleRequestID AS requests
FROM tblRequests requests WITH (NOLOCK)
LEFT OUTER JOIN EC_OFFICE office WITH (NOLOCK) ON requests.tiOfficeID = office.OFFICE_ID
LEFT OUTER JOIN tblRequesters requesters WITH (NOLOCK) ON requests.iRequesterID = requesters.iRequesterID
WHERE requests.vcVisibleRequestID = ?
  AND office.OFFICE_CODE = ?
"""


class AxisClient:
    def __init__(
        self,
        connection,
        excluded_statuses: tuple[str, ...] = ("Closed", "Completed"),
    ):
        self.connection = connection
        self.excluded_statuses = excluded_statuses

    def _build_query(self, base_query: str) -> str:
        if not self.excluded_statuses:
            return base_query

        placeholders = ", ".join("?" for _ in self.excluded_statuses)
        return f"{base_query.rstrip()}\n  AND requests.vcRequestStatus NOT IN ({placeholders})\n"

    def _build_params(self, request_id: str) -> tuple[str, ...]:
        office_code = request_id.split("-")[0]
        return (request_id, office_code, *self.excluded_statuses)

    def _fetch_one(self, query: str, request_id: str):
        final_query = self._build_query(query)
        params = self._build_params(request_id)
        cursor = self.connection.cursor()
        LOGGER.debug("Executing AXIS query:\n%s", final_query)
        LOGGER.debug("AXIS query params: %s", params)
        cursor.execute(final_query, params)
        row = cursor.fetchone()
        return self._as_dict(cursor, row) if row else None

    def _fetch_all(self, query: str, request_id: str) -> list[dict]:
        final_query = self._build_query(query)
        params = self._build_params(request_id)
        cursor = self.connection.cursor()
        LOGGER.debug("Executing AXIS query:\n%s", final_query)
        LOGGER.debug("AXIS query params: %s", params)
        cursor.execute(final_query, params)
        rows = cursor.fetchall()
        return [self._as_dict(cursor, row) for row in rows]

    @staticmethod
    def _as_dict(cursor, row) -> dict:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))

    def fetch_parent_request(self, request_id: str):
        return self._fetch_one(PARENT_REQUEST_QUERY, request_id)

    def fetch_ministry_request(self, request_id: str):
        return self._fetch_one(MINISTRY_REQUEST_QUERY, request_id)

    def fetch_applicants(self, request_id: str):
        return self._fetch_all(APPLICANTS_QUERY, request_id)

    def fetch_contact_information(self, request_id: str):
        return self._fetch_all(CONTACT_INFORMATION_QUERY, request_id)
