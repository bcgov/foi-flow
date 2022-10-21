import {
    httpGETRequest,
    httpPOSTRequest,
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
    setFOIAttachmentListLoader,
    setRequestRecords,
    setFOILoader,
  } from "../../../actions/FOI/foiRequestActions";
  import {fnDone} from './foiServicesUtil';
  import UserService from "../../../services/UserService";
  import { replaceUrl } from "../../../helper/FOI/helper";

 export const fetchFOIRecords = (requestId, ministryId, ...rest) => {
  if (ministryId) {
    const done = fnDone(rest);
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_GET_RECORDS,
     "<ministryrequestid>", ministryId),
     "<requestid>", requestId);
    return (dispatch) => {
      httpGETRequest(apiUrl, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            dispatch(setRequestRecords(res.data));
            dispatch(setFOIAttachmentListLoader(false));
            done(null, res.data);

          } else {
            console.log("Error in fetching records", res);
            dispatch(serviceActionError(res));
            dispatch(setFOIAttachmentListLoader(false));
          }
        })
        .catch((error) => {
          console.log("Error in fetching records", error);
          dispatch(serviceActionError(error));
          dispatch(setFOIAttachmentListLoader(false));
          done(error);
        });
    };
  }
};

  export const saveFOIRecords = (requestId, ministryId, data, ...rest) => {
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_GET_RECORDS,
     "<ministryrequestid>", ministryId),
     "<requestid>", requestId);
    return (dispatch) => {
      postRecord(dispatch, apiUrl, data, "Error in posting records", rest);
    };
  };

  const postRecord = (dispatch, apiUrl, data, errorMessage, rest) => {
    const done = fnDone(rest);
    httpPOSTRequest(apiUrl, data)
        .then((res) => {
          if (res.data) {
            dispatch(setFOIAttachmentListLoader(false));
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            throw new Error(errorMessage);
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
}