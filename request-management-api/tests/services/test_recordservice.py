from types import SimpleNamespace

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.recordservice import recordservice


def test_update_delete_clears_loaded_group_relationships_before_save(monkeypatch):
    service = recordservice()
    fake_record = SimpleNamespace(
        recordid=26138,
        groups=[SimpleNamespace(document_set_id=99)],
    )

    monkeypatch.setattr(
        "request_api.services.recordservice.FOIRequestRecord.getrecordsbyid",
        lambda recordids: [fake_record],
    )
    monkeypatch.setattr(
        service,
        "_create_historical_record",
        lambda record: object(),
    )
    monkeypatch.setattr(
        service,
        "_prepare_record_update",
        lambda record, requestdata, userid: record,
    )

    removed_record_ids = []

    def fake_remove_records_from_all_groups(record_ids):
        removed_record_ids.append(record_ids)

    monkeypatch.setattr(
        "request_api.services.recordservice.FOIRequestRecordGroups.remove_records_from_all_groups",
        fake_remove_records_from_all_groups,
    )

    def fake_create(records, historical_records):
        assert records[0].groups == []
        return DefaultMethodResult(True, "Records saved/updated", -1, {})

    monkeypatch.setattr(
        "request_api.services.recordservice.FOIRequestRecord.create",
        fake_create,
    )
    monkeypatch.setattr(
        service,
        "_handle_doc_reviewer_api",
        lambda ministryrequestid, records_data, requestdata: DefaultMethodResult(
            True,
            "Record deleted in Doc Reviewer DB",
            -1,
            [],
        ),
    )

    result = service.update(
        21980,
        21965,
        {
            "records": [
                {
                    "recordid": 26138,
                    "documentmasterid": 38226,
                    "filepath": "https://example.com/record.pdf",
                }
            ],
            "isdelete": True,
        },
        "tester",
    )

    assert result.success is True
    assert removed_record_ids == [{26138}]
