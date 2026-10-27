"""Applicant profile dumps must preserve stored JSON without dict coercion."""

from types import SimpleNamespace

import pytest

from request_api.models.FOIRequestApplicants import ApplicantProfileBaseSchema


@pytest.mark.parametrize('many', [False, True])
@pytest.mark.parametrize('history', [
    None, [], [{'request': 'A', 'status': 'Closed'}],
    [{'request': 'A', 'status': 'Closed', 'year': 2020}],
    [{'request': 'A', 'status': 'Closed'}, {'request': 'B', 'status': None}],
    [{'request': 'A', 'metadata': {'tags': ['x', None], 'count': 2}}],
    {'legacy': [1, False, None]}, 'legacy', 12, False,
])
def test_history_dump_preserves_json(app, many, history):
    with app.app_context():
        applicant = SimpleNamespace(request_history=history)
        result = ApplicantProfileBaseSchema(many=many).dump([applicant] if many else applicant)
        dumped = result[0]['requestHistory'] if many else result['requestHistory']
        assert dumped == history
        assert type(dumped) is type(history)
