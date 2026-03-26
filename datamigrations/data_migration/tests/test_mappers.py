from mappers.applicants import map_applicant, map_applicant_mapping
from mappers.contact_information import map_contact_rows
from mappers.requests import map_ministry_request, map_parent_request, map_raw_request


def test_map_parent_request_builds_foirequest_payload() -> None:
    payload = map_parent_request(
        {
            "requestType": "general",
            "receivedDate": "2020-01-02 10:00:00",
            "requestdescription": "records",
            "reqDescriptionFromDate": "",
            "reqDescriptionToDate": "",
            "receivedMode": "Email",
            "category": "Media",
            "filenumber": "XGR-2020-10982",
        }
    )

    assert payload["migrationreference"] == "XGR-2020-10982"
    assert payload["requesttype"] == "general"
    assert payload["receiveddate"].isoformat() == "2020-01-02T10:00:00"


def test_map_ministry_request_preserves_json_fields() -> None:
    payload = map_ministry_request(
        {
            "filenumber": "XGR-2020-10982",
            "requestdescription": "records",
            "reqDescriptionFromDate": "",
            "reqDescriptionToDate": "",
            "requestProcessStart": "2020-01-02 10:00:00",
            "dueDate": "2020-01-30 16:00:00",
            "cfrDueDate": "",
            "requestPageCount": "5",
            "linkedRequests": '[{"XGR-2020-00001":"CFD"}]',
            "identityVerified": '"yes"',
            "originalDueDate": "2020-01-28 16:00:00",
        }
    )

    assert payload["requestpagecount"] == 5
    assert payload["linkedrequests"] == [{"XGR-2020-00001": "CFD"}]
    assert payload["identityverified"] == "yes"


def test_map_raw_request_builds_raw_payload() -> None:
    payload = map_raw_request(
        {
            "filenumber": "XGR-2020-10982",
            "status": "Open",
            "requestdescription": "records",
            "receivedMode": "Email",
            "linkedRequests": '[{"XGR-2020-00001":"CFD"}]',
        }
    )

    assert payload["axisrequestid"] == "XGR-2020-10982"
    assert payload["sourceofsubmission"] == "Email"
    assert payload["requestrawdata"]["requestdescription"] == "records"
    assert payload["linkedrequests"] == [{"XGR-2020-00001": "CFD"}]


def test_map_applicant_sets_main_applicant_fields() -> None:
    applicant_payload = map_applicant(
        {
            "firstName": "Jane",
            "lastName": "Doe",
            "middleName": "Q",
            "birthDate": "1990-01-01 00:00:00",
            "businessName": "ACME",
        }
    )
    mapping_payload = map_applicant_mapping(
        {
            "requestid": "XGR-2020-10982",
            "MainApplicant": 1,
        },
        foirequestapplicantid=7,
        foirequest_id=11,
        foirequestversion_id=1,
    )

    assert applicant_payload["dob"].isoformat() == "1990-01-01T00:00:00"
    assert mapping_payload["requestor_type_name"] == "Self"
    assert mapping_payload["migrationreference"] == "XGR-2020-10982"


def test_map_contact_rows_emits_email_and_phone_records() -> None:
    rows = map_contact_rows(
        {
            "email": "jane@example.com",
            "address1": "",
            "address2": "",
            "city": "",
            "zipcode": "",
            "work1": "",
            "work2": "",
            "mobile": "2505550101",
            "home": "",
            "country": "Canada",
            "province": "BC",
            "requests": "XGR-2020-10982",
        },
        foirequest_id=11,
        foirequestversion_id=1,
    )

    assert [row["dataformat"] for row in rows] == ["email", "phone"]
    assert rows[0]["value"] == "jane@example.com"
    assert rows[1]["value"] == "2505550101"
