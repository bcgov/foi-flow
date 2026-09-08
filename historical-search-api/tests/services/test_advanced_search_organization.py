import importlib
from unittest.mock import patch

from request_api.models.factRequestDetails import factRequestDetails


fact_request_details_module = importlib.import_module(
    "request_api.models.factRequestDetails"
)


def _organization_search_params(keyword):
    return {
        "search": "businessName",
        "keywords": [keyword],
        "requesttype": [],
        "requestflags": [],
        "daterangetype": None,
        "sortingitem": "receiveddate",
        "sortingorder": "desc",
        "size": 100,
        "page": 1,
    }


def test_historical_organization_search_uses_company_bind_parameter():
    params = _organization_search_params("Kyle's Law Firm")

    with patch.object(
        fact_request_details_module,
        "db",
    ) as mock_db:
        mock_db.session.execute.return_value = []

        result = factRequestDetails.getadvancedsearchresults(
            False,
            params,
        )

        assert result == {
            "results": [],
            "count": 0,
        }

        mock_db.session.execute.assert_called_once()

        args = mock_db.session.execute.call_args.args
        query = str(args[0])
        queryparams = args[1]

        assert 'FROM public."dimRequesters" r' in query
        assert (
            'r.requesterid = '
            'public."ClosedRequestDetailsPost2018".requesterid'
            in query
        )
        assert "LOWER(r.company)" in query
        assert ":businessname_0" in query

        # User-entered organization text must remain a bound
        # parameter and must not be interpolated into the SQL.
        assert "Kyle's Law Firm" not in query

        assert queryparams == {
            "businessname_0": "%Kyle's Law Firm%",
        }

        mock_db.session.close.assert_called_once()


def test_historical_organization_search_trims_keyword():
    params = _organization_search_params(
        "  Kyle's Law Firm  "
    )

    with patch.object(
        fact_request_details_module,
        "db",
    ) as mock_db:
        mock_db.session.execute.return_value = []

        factRequestDetails.getadvancedsearchresults(
            False,
            params,
        )

        args = mock_db.session.execute.call_args.args
        queryparams = args[1]

        assert queryparams == {
            "businessname_0": "%Kyle's Law Firm%",
        }
