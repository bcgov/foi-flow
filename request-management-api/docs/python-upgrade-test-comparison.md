# Python upgrade full-suite comparison

Baseline: original application source e24fb26f8 on its recorded Python 3.10 image. Only synthetic test configuration/HTTP fixtures and compatible transaction-fixture code were overlaid; application source stayed unchanged.

Candidate: Python 3.13.17 after code review fixes, using disposable dependencies. No deployed data was used.

Baseline: {'error': 1, 'passed': 157, 'failure': 76}.
Candidate: {'error': 1, 'passed': 230, 'failure': 70}.
Previously passing baseline tests newly failing: 0. Previously failing cases now passing: 6.

Focused CI gate: 118 passed, two explicitly deselected stale baseline scheduler SQL assertions. The full legacy suite remains red; this comparison does not establish untested integrations or security acceptance.

## Baseline failures now passing

- `tests.restapi.test_communicationwrapperservice.TestResolveOwnershipCoords.test_resolves_from_schema_dump_with_dotted_bcgovcode`
- `tests.restapi.test_communicationwrapperservice.TestResolveOwnershipCoords.test_falls_back_to_bare_bcgovcode_key`
- `tests.restapi.test_communicationwrapperservice.TestResolveOwnershipCoords.test_fallback_sql_supplies_bcgovcode_when_schema_lacks_it`
- `tests.restapi.test_communicationwrapperservice.TestResolveOwnershipCoords.test_returns_empty_when_nothing_resolvable`
- `tests.restapi.test_communicationwrapperservice.TestResolveOwnershipCoords.test_historical_query_failure_does_not_break_resolution`
- `tests.restapi.test_communicationwrapperservice.TestResolveOwnershipCoords.test_null_historical_rows_are_ignored`

## Remaining failures and collection errors

All cases below also failed or errored on the isolated baseline. Their assertions are retained.

- `.tests.services.test_publication_completed_consumer`: collection failure
- `tests.restapi.test_fee_api.test_create_payment`: RuntimeError: no running event loop
- `tests.restapi.test_fee_api.test_complete_payment`: AttributeError: 'NoneType' object has no attribute 'get'
- `tests.restapi.test_fee_api.test_generate_receipt`: AttributeError: 'NoneType' object has no attribute 'get'
- `tests.restapi.test_foiassignees_api.test_get_foiassigneesforgeneralopen`: requests_mock.exceptions.NoMockAddress: No mock address: GET http://oidc:8080/auth/admin/realms/test/groups/upgrade-intake-group/members
- `tests.restapi.test_foiassignees_api.test_get_foiassigneesforgeneralcfr`: requests_mock.exceptions.NoMockAddress: No mock address: GET http://oidc:8080/auth/admin/realms/test/groups/upgrade-intake-group/members
- `tests.restapi.test_foiassignees_api.test_get_foiassigneesforpersonalopen`: requests_mock.exceptions.NoMockAddress: No mock address: GET http://oidc:8080/auth/admin/realms/test/groups/upgrade-intake-group/members
- `tests.restapi.test_foiassignees_api.test_get_foiassigneesforgroup`: requests_mock.exceptions.NoMockAddress: No mock address: GET http://oidc:8080/auth/admin/realms/test/groups/upgrade-intake-group/members
- `tests.restapi.test_foiaudit_api.test_get_foiauditfordesccase1`: KeyError: 'id'
- `tests.restapi.test_foiaudit_api.test_get_foiauditfordesccase2`: KeyError: 'id'
- `tests.restapi.test_foicfrfee_api.test_foicfrfees_create`: KeyError: 'id'
- `tests.restapi.test_foicfrfee_api.test_foicfrfees_sanction`: KeyError: 'id'
- `tests.restapi.test_foicfrfee_api.test_foicfrfees_get`: KeyError: 'id'
- `tests.restapi.test_foicomment_api.test_foirawcomment`: KeyError: 'id'
- `tests.restapi.test_foicomment_api.test_foirawcommentdisable`: KeyError: 'id'
- `tests.restapi.test_foicomment_api.test_foirawcommentupdate`: KeyError: 'id'
- `tests.restapi.test_foicomment_api.test_foiministrycomment`: KeyError: 'id'
- `tests.restapi.test_foicomment_api.test_foiministrycommentdisable`: KeyError: 'id'
- `tests.restapi.test_foicomment_api.test_foiministrycommentupdate`: KeyError: 'id'
- `tests.restapi.test_foicomment_api.test_foiministrycommentmigrate`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foiministrydocument_list`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foiministrydocument_rename`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foiministrydocument_replace`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foiministrydocument_delete`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foiministrydocument_create`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foirawdocument_list`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foirawdocument_rename`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foirawdocument_replace`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foirawdocument_delete`: KeyError: 'id'
- `tests.restapi.test_foidocument_api.test_foirawdocument_create`: KeyError: 'id'
- `tests.restapi.test_foiextension_api.test_foiministryextension_list`: KeyError: 'id'
- `tests.restapi.test_foiextension_api.test_foiministryextension_create`: KeyError: 'id'
- `tests.restapi.test_foiextension_api.test_foiministryextension_edit`: KeyError: 'id'
- `tests.restapi.test_foiextension_api.test_foiministryextension_delete`: KeyError: 'id'
- `tests.restapi.test_foimasterdata_api.test_post_fois3storagerequests`: TypeError: string indices must be integers, not 'str'
- `tests.restapi.test_foinotification_api.test_post_get_foirequest_general_cfr_notification`: KeyError: 'id'
- `tests.restapi.test_foinotification_api.test_dismiss_foirequest_general_cfr_notification`: KeyError: 'id'
- `tests.restapi.test_foinotification_api.test_dismissall_foirequest_general_cfr_notification`: KeyError: 'id'
- `tests.restapi.test_foinotification_api.test_foirequest_general_cfr_notification_reminder`: KeyError: 'id'
- `tests.restapi.test_foirecord_api.test_foiministrydocument_list`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_personal`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_closed`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_cfr`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_cfrtoopen`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_cfrtoreview`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_reviewtoconsult`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_reviewtominsignoff`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_consulttoreview`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_cfr_assignment`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_cfr_division`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_cfr_document`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_post_foirequest_general_close`: KeyError: 'id'
- `tests.restapi.test_foirequest_api.test_get_foirequestqueuewithoutheader`: assert 401 == 500
- `tests.restapi.test_foisystemcomment_api.test_createrawrequest_state_comment_intakeinprogres_to_open`: KeyError: 'id'
- `tests.restapi.test_foisystemcomment_api.test_createrawrequest_division_comment`: KeyError: 'id'
- `tests.restapi.test_foiwatcher_api.test_foirawwatcher`: KeyError: 'id'
- `tests.restapi.test_foiwatcher_api.test_foiministrywatcher`: KeyError: 'id'
- `tests.restapi.test_rawrequest_api.test_post_foirawrequests`: KeyError: 'id'
- `tests.restapi.test_rawrequest_api.test_post_foirawrequestspii`: KeyError: 'id'
- `tests.restapi.test_rawrequest_api.test_post_foirawrequestscancel`: KeyError: 'id'
- `tests.restapi.test_rawrequest_api.test_post_foirawrequestsredirect`: KeyError: 'id'
- `tests.restapi.test_rawrequest_api.test_post_foirequest_general`: KeyError: 'id'
- `tests.services.email.test_senderservice_logging.test_send_logs_email_metadata`: assert False
- `tests.services.test_dashboard_services.test_get_requests_dashboard`: RuntimeError: Working outside of request context.
- `tests.services.test_dashboard_services.test_get_ministryrequests_dashboard`: RuntimeError: Working outside of request context.
- `tests.services.test_publication_completed_stream_consumer.test_read_once_dispatches_unpublish_completion_by_payload_kind_and_acks_success`: AssertionError: assert [] == [('publicatio...000000000-2')]
- `tests.services.test_publication_scheduler.test_getopeninforecordsforprepublishing_filters_publishable_rows`: assert 'oi.processingstatus is NULL' in "\n                SELECT\n                    oi.foiopeninforequestid as openinfoid,\n                    oi.created_...->>'amountpaid')::Numeric, 0),\n
- `tests.services.test_publication_scheduler.test_getpdrecordsforprepublishing_filters_publishable_rows`: AssertionError: assert 'pd.processingstatus IS NULL' in '\n                SELECT\n                    pd.proactivedisclosureid,\n                    pd.created_at,\n        ...                  pd.si
- `tests.services.test_requestextension_services.test_create_extension`: TypeError: 'NoneType' object is not subscriptable
- `tests.services.test_requestextension_services.test_get_request_extensions`: TypeError: 'NoneType' object is not subscriptable

Full evidence: `/tmp/request-api-python-upgrade/baseline-comparison/`, `/tmp/request-api-python-upgrade/candidate-full-reviewed/`. Focused evidence: `/tmp/request-api-python-upgrade/focused-reviewed/`.
