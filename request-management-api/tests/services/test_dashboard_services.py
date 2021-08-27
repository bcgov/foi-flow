import pytest
from request_api.services.dashboardservice import dashboardservice
import json

def test_get_requests_dashboard(session): 
      groups = ["Intake Team","Flex Team"] 
      queue = dashboardservice.getrequestqueue(groups)
      for item in queue:
        assert item["idNumber"]