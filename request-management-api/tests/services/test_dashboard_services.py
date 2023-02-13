import pytest
from request_api.services.dashboardservice import dashboardservice
import json
from request_api.utils.enums import MinistryTeamWithKeycloackGroup

def test_get_requests_dashboard(session): 
      groups = ["Intake Team","Flex Team"] 
      queue = dashboardservice().getrequestqueuepagination(groups)
      assert queue.data is not None

def test_get_ministryrequests_dashboard(session): 
      groups = MinistryTeamWithKeycloackGroup.list() 
      queue = dashboardservice().getrequestqueuepagination(groups)
      assert queue.data is not None        