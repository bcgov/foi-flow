import {
    httpPOSTRequest,
    httpGETRequest,
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
    setCorrespondenceEmails,
  } from "../../../actions/FOI/foiRequestActions";
  import UserService from "../../../services/UserService";
  import { replaceUrl } from "../../../helper/FOI/helper";
  import { catchError, fnDone } from "./foiServicesUtil";
  
export const fetchCorrespondenceEmailList = (ministryId, requestId, ...rest) => { 
  const done = fnDone(rest); 
    let apiUrl = '';
    if (!ministryId) ministryId = 'None'
    if (!requestId) requestId = 'None'

    apiUrl = replaceUrl(
        API.FOI_GET_REQUEST_CORRESPONDENCE_EMAILS,
        "<ministryid>",
        ministryId
      );
    apiUrl = replaceUrl(apiUrl, "<rawrequestid>", requestId);
    return (dispatch) => {
      httpGETRequest(apiUrl, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {      
            done(null,res.data);
          } else {
            console.log("Error in fetching correspondence email list", res);
            dispatch(serviceActionError(res));
          }
        })
        .catch((error) => {
          catchError(error, dispatch);
        });
    };
  };
  
  export const saveCorrespondenceEmail = (ministryId, requestId, data, ...rest) => {
    const done = fnDone(rest);
    let apiUrl = API.FOI_POST_REQUEST_CORRESPONDENCE_EMAIL;
    if (!ministryId) ministryId = 'None';
    if (!requestId) requestId = 'None';

    apiUrl = replaceUrl(
      API.FOI_POST_REQUEST_CORRESPONDENCE_EMAIL,
      "<ministryid>",
      ministryId
    );
    apiUrl = replaceUrl(apiUrl, "<rawrequestid>", requestId);
    return (dispatch) => {
      httpPOSTRequest(apiUrl, data)
        .then((res) => {
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            throw new Error("Error in updating correspondence email list");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done(error);
        });
    };
  };