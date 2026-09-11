import importlib
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy.dialects import postgresql

from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest


foi_ministry_requests_module = importlib.import_module(
    "request_api.models.FOIMinistryRequests"
)


def _compile_postgres(condition):
    return str(
        condition.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_raw_organization_search_uses_business_name_fields():
    params = {
        "search": "businessName",
        "keywords": ["Kyle's Law Firm"],
    }

    condition = FOIRawRequest.getfilterforsearch(params)
    sql = _compile_postgres(condition)

    assert "businessName" in sql
    assert "contactInfo" in sql
    assert "requestid" not in sql.lower()


def test_raw_organization_search_supports_multiple_keywords():
    params = {
        "search": "businessName",
        "keywords": ["Kyle", "Law Firm"],
    }

    condition = FOIRawRequest.getfilterforsearch(params)
    sql = _compile_postgres(condition)

    assert "businessName" in sql
    assert "contactInfo" in sql
    assert sql.lower().count("like") >= 4


def test_processed_organization_search_uses_applicant_business_name():
    params = {
        "search": "businessName",
        "keywords": ["Kyle's Law Firm"],
    }

    # FOIMinistryRequest.findfield() creates an alias for an unrelated
    # model before evaluating its field map. Creating that alias forces
    # SQLAlchemy to configure the entire application mapper graph.
    # Stub aliased() here because this focused test only needs to verify
    # the Organization field mapping and generated search expression.
    with patch.object(
        foi_ministry_requests_module,
        "aliased",
        side_effect=lambda model: model,
    ):
        assignee = SimpleNamespace(
            firstname="Test",
            lastname="User",
        )

        condition = FOIMinistryRequest.getfilterforsearch(
            params,
            assignee,
            assignee,
        )

    sql = _compile_postgres(condition)

    assert "businessname" in sql.lower()
    assert "axisrequestid" not in sql.lower()
