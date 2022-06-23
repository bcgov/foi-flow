import { httpOpenPOSTRequest, httpOpenGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {replaceUrl} from "../../../helper/FOI/helper";

import axios from 'axios';
jest.mock('axios');

test('Unit test for api request notes', () => {
  const notes = [{"userId":"foisuper@idir","commentId":59,"text":"foisuper@idir changed the state of the request to Open","dateUF":"2021-12-14T22:22:22.756829+00:00","date":"2021 Dec 14 | 02:22 PM","parentCommentId":null,"commentTypeId":2,"replies":[]},{"userId":"foisuper@idir","commentId":37,"text":"Super User changed the state of the request to Call For Records","dateUF":"2021-12-13T22:09:16.215155+00:00","date":"2021 Dec 13 | 02:09 PM","parentCommentId":null,"commentTypeId":2,"replies":[]},{"userId":"foisuper@idir","commentId":31,"text":"Super User changed the state of the request to Open","dateUF":"2021-12-13T19:32:30.391796+00:00","date":"2021 Dec 13 | 11:32 AM","parentCommentId":null,"commentTypeId":2,"replies":[]},{"userId":"foisuper@idir","commentId":30,"text":"Super User changed the state of the request to Intake in Progress","dateUF":"2021-12-13T19:17:12.906769+00:00","date":"2021 Dec 13 | 11:17 AM","parentCommentId":null,"commentTypeId":2,"replies":[]},{"userId":"foisuper@idir","commentId":29,"text":"Super User changed the state of the request to Closed","dateUF":"2021-12-13T19:07:00.505782+00:00","date":"2021 Dec 13 | 11:07 AM","parentCommentId":null,"commentTypeId":2,"replies":[]}]
  const resp = {data: notes};
  axios.get.mockResolvedValue(resp);
  let apiUrl = 
   replaceUrl(
        API.FOI_GET_COMMENT_MINISTRYREQUEST,
       "<ministryrequestid>", 1);
    
  return httpOpenGETRequest(apiUrl).then(response => expect(response.data).toEqual(notes));
});

test('Unit test for api save ministry request note', () => {
  const note = {"ministryrequestid":"4","comment":"<p>test comment</p>"}
  const responseData = {"id":68,"message":"Comment added","status":true}
  const resp = {data: responseData};
  axios.post.mockResolvedValue(resp);
  let apiUrl = API.FOI_POST_COMMENT_MINISTRYREQUEST;
    
  return httpOpenPOSTRequest(apiUrl, note).then(response => expect(response.data).toEqual(responseData));
});

test('Unit test for api edit ministry request note', () => {
    const note = {"comment":"<p>test comment - 12</p>"}
    const responseData = {"id":"68","message":"Comment updated","status":true}
    const resp = {data: responseData};
    axios.post.mockResolvedValue(resp);
    let apiUrl = replaceUrl(replaceUrl(
        API.FOI_PUT_COMMENT_MINISTRYREQUEST,
      ), "<ministryrequestid>", 1);
      
    return httpOpenPOSTRequest(apiUrl, note).then(response => expect(response.data).toEqual(responseData));
  });

  test('Unit test for api delete ministry request note', () => {
    const note = {}
    const responseData = {"id":"67","message":"Comment disabled","status":true}
    const resp = {data: responseData};
    axios.post.mockResolvedValue(resp);
    let apiUrl =  replaceUrl(replaceUrl(
        API.FOI_DELETE_COMMENT_MINISTRYREQUEST,
      ), "<commentid>", 67);
      
    return httpOpenPOSTRequest(apiUrl, note).then(response => expect(response.data).toEqual(responseData));
  });