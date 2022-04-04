import { httpGETRequest, httpPOSTRequest } from "../../httpRequestHandler";
  import UserService from "../../../services/UserService";
import API from "../../endpoints";
  import {
    serviceActionError,
    setRequestExtensions,
  } from "../../../actions/FOI/foiRequestActions";  
  import { replaceUrl } from "../../../helper/FOI/helper";
  import { fnDone, catchError } from "./foiServicesUtil";

export const fetchExtensionReasons = async ({
  callback,
  dispatch
}) => {
  const apiUrl = API.FOI_GET_EXTENSION_REASONS;

  httpGETRequest(apiUrl, {}, UserService.getToken())
    .then((res) => {
      if (res.data) {
        callback(res.data);
      } else {
        dispatch(serviceActionError(res));
      }
    })
    .catch((error) => {
      dispatch(serviceActionError(error));
    });
};

export const fetchExtension = ({extensionId, callback, errorCallback, dispatch}) => {
  const apiUrl = replaceUrl(
    API.FOI_GET_EXTENSION,
    "<extensionId>",
    extensionId
  );

  httpGETRequest(apiUrl, {}, UserService.getToken())
    .then((res) => {
      callback(res.data);
    })
    .catch((error) => {
      dispatch(serviceActionError(error));
      errorCallback("Internal server error occurred while fetching extension details")
    });
};

export const fetchExtensions = ({
  ministryId,
  errorCallback = null,
  dispatch,
}) => {
  const apiUrl = replaceUrl(
    API.FOI_GET_EXTENSIONS,
    "<ministryrequestid>",
    ministryId
  );
  httpGETRequest(apiUrl, {}, UserService.getToken())
    .then((res) => {
      if (res.data) {
        dispatch(setRequestExtensions(res.data));
      } else {
        console.log("Error in fetching attachment list", res);
        dispatch(serviceActionError(res));
      }
    })
    .catch((error) => {
      console.log("Error in fetching attachment list", error);
      dispatch(serviceActionError(error));
      if (errorCallback) {
        errorCallback();
      }
    });
};

export const createExtensionRequest = ({
  data,
  requestId,
  ministryId,
  callback,
  errorCallback,
  dispatch,
}) => {
  if (!ministryId) {
    dispatch(serviceActionError("No request id"));
  }

  const apiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_EXTENSION, "<requestid>", requestId),
    "<ministryrequestid>",
    ministryId
  );

  httpPOSTRequest(apiUrl, data)
    .then((res) => {
      if (res.data) {
        callback(res.data);
      } else {
        dispatch(serviceActionError(res));
        throw new Error();
      }
    })
    .catch((error) => {
      catchError(error, dispatch);
      errorCallback("An error occured while trying to save this extension");
    });
};

export const addAXISExtensions = (data, ministryId, ...rest) => {
  const done = fnDone(rest);  
  let apiUrl = replaceUrl(
    API.FOI_POST_AXIS_EXTENSIONS,
    "<ministryrequestid>",
    ministryId
  );  

  return (dispatch) => {
    httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data) {
          console.log("Extensions saved successfully!");
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error in saving request extensions details for the ministry# ${ministryId}`);
        }
      })
      .catch((error) => {
        done(error);
        catchError(error, dispatch);
      });
  };
};

export const updateExtensionRequest = ({
  data,
  extensionId,
  ministryId,
  requestId,
  callback,
  errorCallback,
  dispatch,
}) => {

  let apiUrl = API.FOI_POST_UPDATE_EXTENSION;
  apiUrl = replaceUrl(apiUrl, "<requestid>", requestId);
  apiUrl = replaceUrl(apiUrl, "<ministryrequestid>", ministryId);
  apiUrl = replaceUrl(apiUrl, "<extensionid>", extensionId);

  httpPOSTRequest(apiUrl, data)
    .then((res) => {
      if (res.data) {
        callback(res.data);
      } else {
        dispatch(serviceActionError(res));
        throw new Error();
      }
    })
    .catch((error) => {
      catchError(error, dispatch);
      errorCallback("An error occured while trying to save this extension");
    });
};

export const deleteExtensionRequest = ({
  extensionId,
  ministryId,
  requestId,
  callback,
  errorCallback,
  dispatch,
}) => {
  let apiUrl = API.FOI_POST_DELETE_EXTENSION;
  apiUrl = replaceUrl(apiUrl, "<requestid>", requestId);
  apiUrl = replaceUrl(apiUrl, "<ministryrequestid>", ministryId);
  apiUrl = replaceUrl(apiUrl, "<extensionid>", extensionId);

  httpPOSTRequest(apiUrl, {})
    .then((res) => {
      callback(res.data);
    })
    .catch((error) => {
      catchError(error, dispatch);
      errorCallback("An error occured while trying to delete this extension");
    });
};