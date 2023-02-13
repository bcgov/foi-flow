import { httpOpenGETRequest, httpOpenPOSTRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {replaceUrl} from "../../../helper/FOI/helper";

import axios from 'axios';
jest.mock('axios');

test('Unit test for api raw request watcher list', () => {
  const watcherList = [{"watchedby": "foiidir","watchedbygroup": "Intake Team"}, {"watchedby": "testidir","watchedbygroup": "Intake Team"}]
  const resp = {data: watcherList};
  axios.get.mockResolvedValue(resp);
  const apiUrl = replaceUrl(
    API.FOI_GET_RAW_REQUEST_WATCHERS,
    "<requestid>",
    1
  );
  return httpOpenGETRequest(apiUrl).then(response => expect(response.data).toEqual(watcherList));
});

test('Unit test for api ministry request watcher list', () => {
    const watcherList = [{"watchedby": "foiaestidir","watchedbygroup": "AEST Ministry Team"}, {"watchedby": "aesttestidir","watchedbygroup": "AEST Ministry Team"}]
    const resp = {data: watcherList};
    axios.get.mockResolvedValue(resp);
    const apiUrl = replaceUrl(
      API.FOI_GET_MINISTRY_REQUEST_WATCHERS,
      "<ministryid>",
      1
    );
    return httpOpenGETRequest(apiUrl).then(response => expect(response.data).toEqual(watcherList));
  });


  test('Unit test for api add a watcher to the request', () => {
    const watcher = {
        "ministryrequestid":1,
        "watchedbygroup": "Intake Team",
        "watchedby": "test@idir",
        "isactive": true
        };
    const responseData = {
        "id": 6,
        "message": "Request added",
        "status": true
      }
    const resp = {data: responseData};
    axios.post.mockResolvedValue(resp);
    let apiUrl = API.FOI_POST_MINISTRY_REQUEST_WATCHERS;
      
    return httpOpenPOSTRequest(apiUrl, watcher).then(response => expect(response.data).toEqual(responseData));
  });

  test('Unit test for api add a watcher to the raw request', () => {
    const watcher = {
        "requestid":1,
        "watchedbygroup": "Intake Team",
        "watchedby": "test@idir",
        "isactive": true
        };
    const responseData = {
        "id": 6,
        "message": "Request added",
        "status": true
      }
    const resp = {data: responseData};
    axios.post.mockResolvedValue(resp);
    let apiUrl = API.FOI_POST_RAW_REQUEST_WATCHERS;
      
    return httpOpenPOSTRequest(apiUrl, watcher).then(response => expect(response.data).toEqual(responseData));
  });