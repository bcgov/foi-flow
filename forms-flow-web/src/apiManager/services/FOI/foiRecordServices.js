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
  if (!ministryId) {
    return () => {};
  }
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

export const retryFOIRecordProcessing = (requestId, ministryId, data, ...rest) => {
  let apiUrl = replaceUrl(replaceUrl(
    API.FOI_RETRY_RECORDS,
   "<ministryrequestid>", ministryId),
   "<requestid>", requestId);
  return (dispatch) => {
    postRecord(dispatch, apiUrl, data, "Error in triggering job retry", rest);
  };
};

export const deleteFOIRecords = (requestId, ministryId, recordId, ...rest) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(replaceUrl(replaceUrl(
    API.FOI_DELETE_RECORDS,
    "<ministryrequestid>", ministryId),
    "<requestid>", requestId),
    "<recordid>", recordId);
    return (dispatch) => {
      postRecord(dispatch, apiUrl, {}, "Error in deleting records", rest);
    };
};

export const deleteReviewerRecords = (filepaths, ...rest) => {
  const done = fnDone(rest);
  let apiUrl = API.DOC_REVIEWER_DELETE_RECORDS;
    return (dispatch) => {
      postRecord(dispatch, apiUrl, filepaths, "Error in deleting records", rest);
    };
};

export const downloadFOIRecordsForHarms = (requestId, ministryId, data, ...rest) => {
  let apiUrl = replaceUrl(replaceUrl(
    API.FOI_DOWNLOAD_RECORDS_FOR_HARMS,
   "<ministryrequestid>", ministryId),
   "<requestid>", requestId);
  return (dispatch) => {
    postRecord(dispatch, apiUrl, data, "Error in posting records", rest, "download");
  };
};

const postRecord = (dispatch, apiUrl, data, errorMessage, rest, type="download") => {
  const done = fnDone(rest);
  httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data && res.data.status) {
          if(type !== "download")
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


