import { httpOpenPOSTRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {replaceUrl} from "../../../helper/FOI/helper";

import axios from 'axios';
jest.mock('axios');

  test('Unit test for api add assignee', () => {
    const assignee = {
        "userType": "iao",
        "assignedGroup": "Intake Team",
        "assignedTo": "foiintakeflex@idir",
        "assignedToFirstName": "Intake",
        "assignedToLastName": "Flex",
        "assignedministrygroup":"LBR Ministry Team"
        };
    const responseData = {
      "id":1,"message":"Request added","ministryRequests":[{"assignedgroup":"Intake Team","assignedministrygroup":"LBR Ministry Team","filenumber":"LBR-2022-230954","id":1,"status":"Call For Records","version":2}],"status":true
      }
    const resp = {data: responseData};
    axios.post.mockResolvedValue(resp);
    const apiUrl = replaceUrl(replaceUrl(replaceUrl(
        API.FOI_REQUEST_ASSIGNEE_API,
        "<requestid>",
        1
      ), "<ministryid>", 1), "<usertype>","iao");      
    return httpOpenPOSTRequest(apiUrl, assignee).then(response => expect(response.data).toEqual(responseData));
  });

  test('Unit test for api add an assignee to the raw request', () => {
    const assignee = {
        "assignedGroup": "Intake Team",
        "assignedTo": "foiintakeflex@idir",
        "assignedToFirstName": "Intake",
        "assignedToLastName": "Flex"
        };
    const responseData = {
      "message": "Request versioned - 2",
      "status": true
      }
    const resp = {data: responseData};
    axios.post.mockResolvedValue(resp);
    const apiUrl = replaceUrl(
      API.FOI_RAWREQUEST_ASSIGNEE_API,
      "<requestid>",
      1
    );      
    return httpOpenPOSTRequest(apiUrl, assignee).then(response => expect(response.data).toEqual(responseData));
  });