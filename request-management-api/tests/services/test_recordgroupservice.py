from types import SimpleNamespace

import request_api.services.records.recordgroupservice as recordgroupservice_module
from request_api.models.FOIRequestRecordGroup import FOIRequestRecordGroup
from request_api.models.FOIRequestRecordGroups import FOIRequestRecordGroups
from request_api.models.db import db
from request_api.services.records.recordgroupservice import recordgroupservice


def test_add_records_deduplicates_rows(monkeypatch):
    captured = {}

    def fake_execute(statement, rows):
        captured["rows"] = rows

    monkeypatch.setattr(db.session, "execute", fake_execute)

    FOIRequestRecordGroups.add_records(77, [4, 4, 2])

    assert captured["rows"] == [
        {"document_set_id": 77, "record_id": 2},
        {"document_set_id": 77, "record_id": 4},
    ]


def test_create_group_removes_records_from_other_groups_before_add(monkeypatch):
    captured = {}
    calls = []

    class FakeGroup:
        def __init__(self, **kwargs):
            self.document_set_id = None
            self.__dict__.update(kwargs)

    def fake_add(group):
        captured["group"] = group

    def fake_flush():
        captured["group"].document_set_id = 170

    monkeypatch.setattr(db.session, "add", fake_add)
    monkeypatch.setattr(db.session, "flush", fake_flush)
    monkeypatch.setattr(db.session, "commit", lambda: None)
    monkeypatch.setattr(
        FOIRequestRecordGroups,
        "remove_from_other_groups",
        lambda document_set_id, record_ids: calls.append(
            ("remove", document_set_id, record_ids)
        ),
    )
    monkeypatch.setattr(
        FOIRequestRecordGroups,
        "add_records",
        lambda document_set_id, record_ids: calls.append(
            ("add", document_set_id, record_ids)
        ),
    )

    group = FOIRequestRecordGroup.create_group.__func__(
        FakeGroup,
        ministry_request_id=15745,
        request_id=15722,
        name="Document Set 4",
        created_by="idir\\tester",
        records=[12850, 12847, 12850],
    )

    assert group is not None
    assert calls == [
        ("remove", 170, {12847, 12850}),
        ("add", 170, {12847, 12850}),
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
        recordgroupservice_module,
        "FOIRequestRecordGroup",
        SimpleNamespace(query=_FakeQuery()),
    )
    monkeypatch.setattr(
        service,
        "fetch_valid_records",
        lambda ministryrequestid, records, requestid: {101, 102},
    )
    monkeypatch.setattr(
        recordgroupservice_module.FOIRequestRecordGroups,
        "get_record_ids",
        lambda document_set_id: next(persisted_sets),
    )

    removed = {}
    added = {}

    monkeypatch.setattr(
        recordgroupservice_module.FOIRequestRecordGroups,
        "remove_from_other_groups",
        lambda document_set_id, record_ids: removed.update(
            {"document_set_id": document_set_id, "record_ids": record_ids}
        ),
    )
    monkeypatch.setattr(
        recordgroupservice_module.FOIRequestRecordGroups,
        "add_records",
        lambda document_set_id, record_ids: added.update(
            {"document_set_id": document_set_id, "record_ids": record_ids}
        ),
    )
    monkeypatch.setattr(
        recordgroupservice_module.db.session,
        "commit",
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
