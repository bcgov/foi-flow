import { httpGETRequest, httpPOSTRequest } from "../../httpRequestHandler";
  import UserService from "../../../services/UserService";
import API from "../../endpoints";
  import {
    serviceActionError,
  } from "../../../actions/FOI/foiRequestActions";
  import { replaceUrl } from "../../../helper/FOI/helper";


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

const fetchExtensions = ({dispatch}) => {
  return;
}

export const saveExtensionRequest = ({data, requestId, callback, errorCallBack, dispatch}) => {
  if(!requestId) {
    dispatch(serviceActionError("No request id"));
  }
  
  const apiUrl = replaceUrl(API.FOI_POST_EXTENSION, "<requestid>", requestId);
  httpPOSTRequest(apiUrl, data)
    .then((res) => {
      if (res.data) {
        fetchExtensions({ dispatch });
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