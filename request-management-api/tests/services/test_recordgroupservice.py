from types import SimpleNamespace

from request_api.models.FOIRequestRecordGroups import FOIRequestRecordGroups
from request_api.services.records.recordgroupservice import recordgroupservice


def test_add_records_deduplicates_rows(monkeypatch):
    captured = {}

    def fake_execute(statement, rows):
        captured["rows"] = rows

    monkeypatch.setattr(
        "request_api.models.FOIRequestRecordGroups.db.session.execute",
        fake_execute,
    )

    FOIRequestRecordGroups.add_records(77, [4, 4, 2])

    assert captured["rows"] == [
        {"document_set_id": 77, "record_id": 2},
        {"document_set_id": 77, "record_id": 4},
    ]


def test_update_returns_persisted_record_ids(monkeypatch):
    service = recordgroupservice()
    group = SimpleNamespace(
        document_set_id=77,
        request_id=12,
        ministry_request_id=34,
        name="Set A",
        updated_by=None,
        updated_at=None,
    )

    class _FakeQuery:
        def filter_by(self, **kwargs):
            return self

        def first(self):
            return group

    persisted_sets = iter([{101}, {101, 102}])

    monkeypatch.setattr(
        "request_api.services.records.recordgroupservice.FOIRequestRecordGroup.query",
        _FakeQuery(),
    )
    monkeypatch.setattr(
        service,
        "fetch_valid_records",
        lambda ministryrequestid, records, requestid: {101, 102},
    )
    monkeypatch.setattr(
        "request_api.services.records.recordgroupservice.FOIRequestRecordGroups.get_record_ids",
        lambda document_set_id: next(persisted_sets),
    )

    removed = {}
    added = {}

    monkeypatch.setattr(
        "request_api.services.records.recordgroupservice.FOIRequestRecordGroups.remove_from_other_groups",
        lambda document_set_id, record_ids: removed.update(
            {"document_set_id": document_set_id, "record_ids": record_ids}
        ),
    )
    monkeypatch.setattr(
        "request_api.services.records.recordgroupservice.FOIRequestRecordGroups.add_records",
        lambda document_set_id, record_ids: added.update(
            {"document_set_id": document_set_id, "record_ids": record_ids}
        ),
    )
    monkeypatch.setattr(
        "request_api.services.records.recordgroupservice.db.session.commit",
        lambda: None,
    )

    result = service.update(
        12,
        34,
        {"documentsetid": 77, "records": [101, 101, 102]},
        "idir\\tester",
    )

    assert result.success is True
    assert removed == {"document_set_id": 77, "record_ids": {102}}
    assert added == {"document_set_id": 77, "record_ids": {102}}
    assert result.data["records"] == [101, 102]
