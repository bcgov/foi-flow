import pytest
from request_api.services.dashboardservice import dashboardservice
import json

def test_get_requests_dashboard(session):  
      queue = dashboardservice.getrequestqueue()
      for item in queue:
        assert item["idNumber"]