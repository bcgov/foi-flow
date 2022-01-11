import { httpGETRequest, httpPOSTRequest } from "../../httpRequestHandler";
  import UserService from "../../../services/UserService";
import API from "../../endpoints";
  import {
    serviceActionError,
    setRequestExtensions,
  } from "../../../actions/FOI/foiRequestActions";
  import { replaceUrl } from "../../../helper/FOI/helper";
  import { postAttachment, fnDone } from "./foiServicesUtil";


export const fetchExtensionReasons = async ({
  callback,
  errorCallBack,
  dispatch
}) => {
  const apiUrl = API.FOI_GET_EXTENSION_REASONS;

  httpGETRequest(apiUrl, {}, UserService.getToken())
    .then((res) => {
      if (res.data) {
        callback(res.data);
      } else {
        errorCallBack();
        dispatch(serviceActionError(res));
      }
    })
    .catch((error) => {
      dispatch(serviceActionError(error));
      errorCallBack();
    });
};

export const fetchExtensions = (
  requestId,
  ...rest
) => {
  const done = fnDone(rest);
  const apiUrl = replaceUrl(
    API.FOI_GET_EXTENSIONS,
    "<requestid>",
    requestId
  );

  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setRequestExtensions(res.data));
          done(null, res.data);
        } else {
          console.log("Error in fetching attachment list", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        console.log("Error in fetching attachment list", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  }
}

export const saveExtensionRequest = ({data, ministryId, callback, errorCallBack, dispatch}) => {
  if(!ministryId) {
    dispatch(serviceActionError("No request id"));
  }
  
  const apiUrl = replaceUrl(
    API.FOI_POST_EXTENSION,
    "<ministryrequestid>",
    ministryId
  );

  httpPOSTRequest(apiUrl, data)
    .then((res) => {
      if (res.data) {
        callback(res.data);
      } else {
        errorCallBack();
        dispatch(serviceActionError(res));
      }
    })
    .catch((error) => {
      dispatch(serviceActionError(error));
      errorCallBack();
    });
};