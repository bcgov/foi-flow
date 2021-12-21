import { httpOpenPOSTRequest } from "../../httpRequestHandler";
import API from "../../endpoints";

import axios from 'axios';
jest.mock('axios');

test('Unit test for api to get OSS header details', () => {
    const requestData = [{"ministrycode":"Misc","requestnumber":"EDUC-2021-26728","filestatustransition":"general","filename":"Testconsent.docx"}]
    const responseData =[{"ministrycode":"Misc","requestnumber":"EDUC-2021-26728","filestatustransition":"general",
    "filename":"Testconsent.docx",
    "filepath":"ossfilepath",
    "authheader":"",
    "amzdate":"","uniquefilename":"8e0334d4-c6fa-4586-b9d9-5e893e8cd4cf.docx"}]
    const resp = {data: responseData};
    axios.post.mockResolvedValue(resp);
    let apiUrl = API.FOI_POST_OSS_HEADER;
      
    return httpOpenPOSTRequest(apiUrl, requestData).then(response => expect(response.data).toEqual(responseData));
  });
  