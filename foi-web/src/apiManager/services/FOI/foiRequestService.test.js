import { httpOpenGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {replaceUrl} from "../../../helper/FOI/helper";

import axios from 'axios';
jest.mock('axios');

test('Unit test for api description history', () => {
  const requestDescriptionHistoryList = 
    [{"createdAt":"2021-09-21 07:45:02","createdBy":"aandrews@idir","description":"new request for the applicant","fromDate":"2021-08-01","status":"Intake in Progress","toDate":"2021-09-16"},{"createdAt":"2021-09-21 07:44:27","createdBy":"aandrews@idir","description":"new request for the applicant","fromDate":"2021-09-01","status":"Intake in Progress","toDate":"2021-09-16"},{"createdAt":"2021-09-17 18:02:06","createdBy":"Online Form","description":"new request for Pepper Potts","fromDate":"2021-09-01","status":"unopened","toDate":"2021-09-16"}];  
  const resp = {data: requestDescriptionHistoryList};
  axios.get.mockResolvedValue(resp);
  const apiUrl = replaceUrl(
    API.FOI_RAW_REQUEST_DESCRIPTION,
    "<requestid>",
    1
  );
  return httpOpenGETRequest(apiUrl).then(response => expect(response.data).toEqual(requestDescriptionHistoryList));
});

test('Unit test for api ministry request list', () => {
  const ministryRequestList = 
  [{"id":1,"requestType":"general","currentState":"Call For Records","receivedDate":"2021 Oct, 06","receivedDateUF":"2021-10-06 00:00:00","assignedGroup":"Intake Team","assignedTo":"jharriet@idir","assignedministrygroup":"AEST Ministry Team","assignedministryperson":null,"cfrstatus":"Select Division","cfrduedate":"2021-10-22T00:00:00+00:00","duedate":"2021-11-19T00:00:00+00:00","idNumber":"AEST-2021-18963","version":3,"ministryrequestid":1,"applicantcategory":"Interest Group","watchers":[]},{"id":2,"requestType":"general","currentState":"Call For Records","receivedDate":"2021 Oct, 06","receivedDateUF":"2021-10-06 07:52:13.394140","assignedGroup":"Intake Team","assignedTo":"aantony@idir","assignedministrygroup":"AEST Ministry Team","assignedministryperson":null,"cfrstatus":"Select Division","cfrduedate":"2021-10-22T00:00:00+00:00","duedate":"2021-11-19T00:00:00+00:00","idNumber":"AEST-2021-32294","version":3,"ministryrequestid":2,"applicantcategory":"Media","watchers":[]}];
  const resp = {data: ministryRequestList};
  axios.get.mockResolvedValue(resp);
  const apiUrl = API.FOI_GET_MINISTRY_REQUESTS_API;
  return httpOpenGETRequest(apiUrl).then(response => expect(response.data).toEqual(ministryRequestList));
});

test('Unit test for api ministry request view', () => {
  const ministryRequest = {"assignedGroup":"Intake Team","assignedTo":"jharriet@idir","category":"Interest Group","categoryid":3,"cfrDueDate":"2021-10-22","currentState":"Call For Records","deliveryMode":"In Person Pick up","deliverymodeid":2,"description":"test request - online --2","dueDate":"2021-11-19","fromDate":"2021-09-01","id":5,"idNumber":"AEST-2021-56756","programareaid":1,"receivedDate":"2021 Oct, 06","receivedDateUF":"2021-10-06 12:33:09.011736","receivedMode":"Online Form","receivedmodeid":4,"requestProcessStart":"2021-10-06","requestType":"general","requeststatusid":2,"selectedMinistries":[{"code":"AEST","name":"Ministry of Advanced Education and Skills Training","selected":"true"}],"toDate":"2021-10-05"};
  const apiUrlgetRequestDetails = replaceUrl(replaceUrl(
    API.FOI_MINISTRYVIEW_REQUEST_API,
    "<requestid>",
    1
  ),"<ministryid>", 1); 
  const resp = {data: ministryRequest};
  axios.get.mockResolvedValue(resp);
  
  return httpOpenGETRequest(apiUrlgetRequestDetails).then(response => expect(response.data).toEqual(ministryRequest));
});