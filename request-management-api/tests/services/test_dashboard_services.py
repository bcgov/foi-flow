import pytest
from request_api.services.dashboardservice import dashboardservice
import json
from request_api.utils.enums import MinistryTeamWithKeycloackGroup

def test_get_requests_dashboard(session): 
      groups = ["Intake Team","Flex Team"] 
      queue = dashboardservice.getrequestqueue(groups)
      for item in queue:
        assert item["idNumber"]

def test_get_ministryrequests_dashboard(session): 
      groups = MinistryTeamWithKeycloackGroup.list() 
      queue = dashboardservice.getrequestqueue(groups)
      for item in queue:
        assert item["idNumber"]        