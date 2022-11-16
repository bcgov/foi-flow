import { httpOpenGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";

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

