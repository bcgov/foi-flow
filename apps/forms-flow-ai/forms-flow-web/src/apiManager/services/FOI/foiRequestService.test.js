import { httpOpenPOSTRequest, httpOpenGETRequest, httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {replaceUrl} from "../../../helper/FOI/helper";

import axios from 'axios';
jest.mock('axios');

test('Unit test for api applicantcategories', () => {
  const applicantcategories = [{"applicantcategoryid": 1, "name": "Business", "description": "Business", "isactive": true}, {"applicantcategoryid": 2,
  "name": "Individual", "description": "Individual", "isactive": true}, {"applicantcategoryid": 3, "name": "Interest Group", "description": "Interest Group", "isactive": true}, {"applicantcategoryid": 4, "name": "Law Firm",
  "description": "Law Firm", "isactive": true}, {"applicantcategoryid": 5, "name": "Media", "description": "Media",
  "isactive": true}, {"applicantcategoryid": 6, "name": "Political Party", "description": "Political Party", "isactive":
  true}, {"applicantcategoryid": 7, "name": "Researcher", "description": "Researcher", "isactive": true},
  {"applicantcategoryid": 8, "name": "Other Governments", "description": "Other Governments", "isactive": true},
  {"applicantcategoryid": 9, "name": "Other Public Body", "description": "Other Public Body", "isactive": true}];
  const resp = {data: applicantcategories};
  axios.get.mockResolvedValue(resp);

  return httpOpenGETRequest(API.FOI_GET_CATEGORIES_API).then(response => expect(response.data).toEqual(applicantcategories));
});

afterEach(() => {
  jest.clearAllMocks();
});

test('Unit test for api delivery model', () => {
  const deliverymodel = [{"description": "Secure File Transfer", "name": "Secure File Transfer", "deliverymodeid": 1, "isactive": true},
  {"description": "In Person Pick up", "name": "In Person Pick up", "deliverymodeid": 2, "isactive": true}];
  const resp = {data: deliverymodel};
  axios.get.mockResolvedValue(resp);
  return httpOpenGETRequest(API.FOI_GET_DELIVERY_MODELIST).then(response => expect(response.data).toEqual(deliverymodel));
});

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