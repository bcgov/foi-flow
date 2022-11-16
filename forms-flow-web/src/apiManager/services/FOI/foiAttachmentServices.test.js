import { httpOpenPOSTRequest, httpOpenGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {replaceUrl} from "../../../helper/FOI/helper";

import axios from 'axios';
jest.mock('axios');

test('Unit test for api attachment log', () => {
  const attachmentsArray = [{"foiministrydocumentid":15,"filename":"Request Review.docx","documentpath":"https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests/EDUC/EDUC-2021-11901/cfr-review/14039a2d-58e8-40c8-a9d9-f8f9ea2eb5be.docx","category":"cfr-review","created_at":"2021 Nov 29 | 12:03 PM","createdby":"foiedu@idir"},{"foiministrydocumentid":16,"filename":"Fee Estimate.docx","documentpath":"https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests/Misc/EDUC-2021-11901/cfr-feeassessed/4bc2d28a-d3aa-487d-a07c-5a3cbd68d8e2.docx","category":"cfr-feeassessed","created_at":"2021 Nov 29 | 12:02 PM","createdby":"foisuper@idir"}]
  const resp = {data: attachmentsArray};
  axios.get.mockResolvedValue(resp);
  let apiUrl = 
   replaceUrl(
        API.FOI_ATTACHMENTS_MINISTRYREQUEST,
       "<ministryrequestid>", 1);
    
  return httpOpenGETRequest(apiUrl).then(response => expect(response.data).toEqual(attachmentsArray));
});

test('Unit test for api replace attachment', () => {
  const attachment = {"filename":"Request Review.docx","documentpath":"https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests/EDUC/EDUC-2021-11901/cfr-review/14039a2d-58e8-40c8-a9d9-f8f9ea2eb5be.docx"};
  const responseData = {
    "id": 15,
    "message": "New Document version created",
    "status": true
    }
  const resp = {data: responseData};
  axios.post.mockResolvedValue(resp);
  let apiUrl = replaceUrl(replaceUrl(
    API.FOI_REPLACE_ATTACHMENT_MINISTRYREQUEST,
    "<ministryrequestid>",
    1
  ), "<documentid>", 15);
    
  return httpOpenPOSTRequest(apiUrl, attachment).then(response => expect(response.data).toEqual(responseData));
});

test('Unit test for api delete attachment', () => {
  const responseData = {
    "id": 15,
    "message": "New Document version created",
    "status": true
    }
  const resp = {data: responseData};
  axios.post.mockResolvedValue(resp);
  let apiUrl = replaceUrl(replaceUrl(
    API.FOI_DELETE_ATTACHMENT_MINISTRYREQUEST,
    "<ministryrequestid>",
    1
  ), "<documentid>", 15);
    
  return httpOpenPOSTRequest(apiUrl, {}).then(response => expect(response.data).toEqual(responseData));
});