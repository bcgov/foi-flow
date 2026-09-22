import json
from unittest.mock import MagicMock, patch

import pytest

from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIRequests import FOIRequest
from request_api.services.external.bpmservice import bpmservice
from request_api.services.external.commonworkflowservice import commonworkflowservice
from request_api.services.paymentservice import paymentservice
from request_api.services.workflowservice import workflowservice
from request_api.utils.enums import StateName


@pytest.fixture(autouse=True)
def _default_camunda(monkeypatch):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", "camunda")


class TestCreateInstance:
    """A brand-new request has no wfinstanceid on record yet, so instance
    creation is routed by WF_DEFAULT_ENGINE. n8n has no createinstance concept
    at all (a single fixed webhook handles every event), so when the default
    engine is n8n, createinstance must be a no-op rather than calling into
    commonworkflowservice (which no longer implements createinstance)."""

    @patch.object(bpmservice, "createinstance")
    def test_new_request_routes_to_camunda_by_default(self, mock_create, monkeypatch):
        monkeypatch.delenv("WF_DEFAULT_ENGINE", raising=False)
        mock_create.return_value = "camunda-instance-id"

        response = workflowservice().createinstance("foi-rawrequest", json.dumps({"id": 42}))

        assert response == "camunda-instance-id"
        mock_create.assert_called_once()

    def test_new_request_is_a_noop_when_default_engine_is_n8n(self, monkeypatch):
        monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")

        response = workflowservice().createinstance("foi-rawrequest", json.dumps({"id": 42}))

        assert response is None

    @patch.object(bpmservice, "createinstance")
    def test_raises_when_engine_returns_none(self, mock_create):
        mock_create.return_value = None
        service = workflowservice()

        with pytest.raises(Exception, match="Unable to create instance for key"):
            service.createinstance("foi-rawrequest", json.dumps({"id": 42}))


class TestPostUnopenedEvent:
    """Engine routing is decided directly from the wfinstanceid passed in:
    a value present means Camunda, empty/None falls back to WF_DEFAULT_ENGINE."""

    @patch.object(FOIRequest, "getrawrequestidbyfoirequestid")
    @patch.object(bpmservice, "unopenedcomplete")
    def test_camunda_request_uses_wfinstanceid(self, mock_call, mock_getrawid):
        mock_getrawid.return_value = 9001
        mock_call.return_value = MagicMock()

        workflowservice().postunopenedevent(1, "camunda-wfid-123", {"assignedGroup": "g", "assignedTo": "u"}, "Open", [])

        mock_call.assert_called_once()
        assert mock_call.call_args[0][0] == "camunda-wfid-123"

    @patch.object(FOIRequest, "getrawrequestidbyfoirequestid")
    @patch.object(commonworkflowservice, "unopenedcomplete")
    def test_n8n_request_with_no_wfinstanceid_calls_engine_with_none(self, mock_call, mock_getrawid, monkeypatch):
        monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")
        mock_getrawid.return_value = 9001
        mock_call.return_value = None

        workflowservice().postunopenedevent(1, None, {"assignedGroup": "g", "assignedTo": "u"}, "Open", [])

        assert mock_call.call_args[0][0] is None

    def test_invalid_wfinstance_returns_without_calling_engine(self):
        assert workflowservice().postunopenedevent(1, None, {}, "Open", []) is None
        assert workflowservice().postunopenedevent(1, "", {}, "Open", []) is None

    @patch.object(commonworkflowservice, "unopenedcomplete")
    def test_rawrequest_status_without_wfinstanceid_routes_to_n8n_default(self, mock_call, monkeypatch):
        monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")
        mock_call.return_value = MagicMock()

        workflowservice().postunopenedevent(4745, None, {"assignedGroup": "g", "assignedTo": "u"}, "Closed", [])

        mock_call.assert_called_once()
        assert mock_call.call_args[0][0] is None


class TestUnopenedSaveReceivesCompleteMetadata:
    """unopenedsave's metadata argument must be the same complete event
    payload (a json.dumps(...) string) every other engine call receives -
    workflowservice stays engine-agnostic and never builds a
    reduced/engine-specific shape for it."""

    @patch.object(workflowservice, "_workflowservice__hasreopened")
    @patch.object(commonworkflowservice, "unopenedsave")
    def test_postunopenedevent_passes_complete_metadata_for_intake_in_progress(self, mock_call, mock_hasreopened, monkeypatch):
        monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")
        mock_call.return_value = MagicMock()
        mock_hasreopened.return_value = False

        workflowservice().postunopenedevent(4745, None, {"assignedGroup": "Intake Team", "assignedTo": "jdoe"}, "Intake in Progress", [])

        mock_call.assert_called_once()
        posted_metadata = json.loads(mock_call.call_args[0][1])
        assert posted_metadata["id"] == 4745
        assert posted_metadata["status"] == "Intake in Progress"
        assert posted_metadata["assignedGroup"] == "Intake Team"
        assert posted_metadata["assignedTo"] == "jdoe"

    @patch.object(commonworkflowservice, "unopenedsave")
    def test_postopenedevent_save_activity_passes_complete_metadata(self, mock_call, monkeypatch):
        # __postopenedevent is the private helper postopenedevent() delegates to for
        # the actual engine call - exercise it directly to isolate the fix (the
        # traceback's failure point) from postopenedevent()'s unrelated DB-heavy setup.
        monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")
        mock_call.return_value = None
        metadata = json.dumps({"id": "CTZ-2026-004813", "assignedGroup": "IAO Team", "assignedTo": "jdoe"})

        workflowservice()._workflowservice__postopenedevent(
            5216, "CTZ-2026-004813", metadata, "foi-iao-open-assignment", None, "save",
        )

        mock_call.assert_called_once_with(None, metadata, "foi-iao-open-assignment")


class TestSyncWfInstanceEngineGate:
    """syncwfinstance() is deferred for n8n: getinstancevariables/searchinstancebyvariable
    aren't implemented for commonworkflowservice yet, so sync is skipped whenever
    WF_DEFAULT_ENGINE is n8n - a single global switch, not a per-request decision."""

    @patch.object(FOIRawRequest, "getworkflowinstancebyraw")
    def test_skips_rawrequest_sync_when_default_is_n8n(self, mock_getwf, monkeypatch):
        monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")

        result = workflowservice().syncwfinstance("rawrequest", 7)

        assert result is None
        mock_getwf.assert_not_called()

    @patch.object(bpmservice, "searchinstancebyvariable")
    @patch.object(FOIRawRequest, "getworkflowinstancebyraw")
    def test_runs_rawrequest_sync_when_default_is_camunda(self, mock_getwf, mock_search):
        # WF_DEFAULT_ENGINE=camunda is the autouse default for this module.
        row = MagicMock()
        row.requestid = 7
        row.wfinstanceid = "camunda-existing-id"
        mock_getwf.return_value = row
        mock_search.return_value = "camunda-existing-id"

        result = workflowservice().syncwfinstance("rawrequest", 7)

        mock_getwf.assert_called()
        assert result == "camunda-existing-id"

    @patch.object(FOIRawRequest, "getworkflowinstancebyraw")
    @patch.object(FOIRequest, "getworkflowinstance")
    def test_skips_ministryrequest_sync_when_default_is_n8n(self, mock_getreqwf, mock_getrawwf, monkeypatch):
        monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")

        result = workflowservice().syncwfinstance("ministryrequest", 55)

        assert result is None
        mock_getrawwf.assert_not_called()
        mock_getreqwf.assert_not_called()


class TestPostOpenedEventIncludesRequestIds:
    """postopenedevent()'s metadata must always carry foiRequestId (the ministry's
    FOIRequests.foirequestid) and rawRequestId (fetched via the existing
    FOIRequest.getrawrequestidbyfoirequestid lookup) for both reopenevent and
    openedcomplete, whether the instance resolves to Camunda or n8n."""

    FOIREQUESTID = 4745
    MINISTRYID = 5216
    RAWREQUESTID = 9001

    def _data(self, ministry_status="Open"):
        return {"ministries": [{
            "id": self.MINISTRYID,
            "foirequestid": self.FOIREQUESTID,
            "version": 3,
            "status": ministry_status,
            "assignedministrygroup": "IAO",
            "filenumber": "CTZ-2026-004813",
        }]}

    @patch.object(FOIMinistryRequest, "getofflinepaymentflag")
    @patch.object(paymentservice, "getpaymentexpirydate")
    @patch.object(workflowservice, "_workflowservice__ispaymentactive")
    @patch.object(workflowservice, "_workflowservice__messagename")
    @patch.object(workflowservice, "_workflowservice__getprevioustatusbyversion")
    @patch.object(FOIRequest, "getrawrequestidbyfoirequestid")
    def _run_postopenedevent(
        self, wfinstanceid, ministry_status, instance_variables,
        mock_getrawid, mock_prevstatus, mock_messagename,
        mock_ispaymentactive, mock_paymentexpiry, mock_offlineflag,
        monkeypatch,
    ):
        mock_getrawid.return_value = self.RAWREQUESTID
        mock_prevstatus.return_value = "Open"
        mock_messagename.return_value = "foi-iao-open-assignment"
        mock_ispaymentactive.return_value = False
        mock_paymentexpiry.return_value = None
        mock_offlineflag.return_value = False
        if wfinstanceid is None:
            monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")
        engine_cls = bpmservice if wfinstanceid else commonworkflowservice

        with patch.object(engine_cls, "getinstancevariables", return_value=instance_variables), \
             patch.object(engine_cls, "openedcomplete", return_value=None) as mock_openedcomplete, \
             patch.object(engine_cls, "reopenevent", return_value=None) as mock_reopenevent:
            workflowservice().postopenedevent(
                self.MINISTRYID, wfinstanceid,
                {"assignedgroup": "IAO", "assignedto": "jdoe"},
                self._data(ministry_status), "Open", "iao", issync=True,
            )
        return mock_openedcomplete, mock_reopenevent

    def _assert_metadata_has_ids(self, mock_call, metadata_index):
        mock_call.assert_called_once()
        metadata = json.loads(mock_call.call_args[0][metadata_index])
        assert metadata["foiRequestId"] == self.FOIREQUESTID
        assert metadata["rawRequestId"] == self.RAWREQUESTID

    def test_camunda_openedcomplete_includes_ids(self, monkeypatch):
        mock_openedcomplete, mock_reopenevent = self._run_postopenedevent(
            "instance-123", "Open", {}, monkeypatch=monkeypatch,
        )
        mock_reopenevent.assert_not_called()
        self._assert_metadata_has_ids(mock_openedcomplete, metadata_index=2)

    def test_camunda_reopenevent_includes_ids(self, monkeypatch):
        mock_openedcomplete, mock_reopenevent = self._run_postopenedevent(
            "instance-123", "Open", {"status": {"value": StateName.closed.value}}, monkeypatch=monkeypatch,
        )
        mock_openedcomplete.assert_not_called()
        self._assert_metadata_has_ids(mock_reopenevent, metadata_index=1)

    def test_n8n_openedcomplete_includes_ids(self, monkeypatch):
        mock_openedcomplete, mock_reopenevent = self._run_postopenedevent(
            None, "Open", {}, monkeypatch=monkeypatch,
        )
        mock_reopenevent.assert_not_called()
        self._assert_metadata_has_ids(mock_openedcomplete, metadata_index=2)

    def test_n8n_reopenevent_includes_ids(self, monkeypatch):
        mock_openedcomplete, mock_reopenevent = self._run_postopenedevent(
            None, "Open", {"status": {"value": StateName.closed.value}}, monkeypatch=monkeypatch,
        )
        mock_openedcomplete.assert_not_called()
        self._assert_metadata_has_ids(mock_reopenevent, metadata_index=1)
