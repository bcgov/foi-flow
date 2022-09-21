import { httpGETRequest, httpPOSTRequest } from "../../httpRequestHandler";
  import UserService from "../../../services/UserService";
import API from "../../endpoints";
  import {
    serviceActionError,
    setRequestCFRForm,
    setRequestCFRFormHistory,
  } from "../../../actions/FOI/foiRequestActions";
  import { replaceUrl } from "../../../helper/FOI/helper";
  import { catchError } from "./foiServicesUtil";
  import { fetchFOIRequestNotesList } from "../../../apiManager/services/FOI/foiRequestNoteServices";
  import _ from 'lodash';

export const fetchCFRForm = (
  ministryId,
  dispatch,
  errorCallback = null
) => {
  const apiUrl = replaceUrl(
    API.FOI_GET_CFR_FORM,
    "<ministryrequestid>",
    ministryId
  );
  httpGETRequest(apiUrl, {}, UserService.getToken())
    .then((res) => {
      if (res.data) {
        if (!_.isEmpty(res.data)) {
          dispatch(setRequestCFRForm(res.data.current));
          dispatch(setRequestCFRFormHistory(res.data.history));
        }
      } else {
        console.log("Error in fetching CFR Form data", res);
        dispatch(serviceActionError(res));
      }
    })
    .catch((error) => {
      console.log("Error in fetching CFR Form data", error);
      dispatch(serviceActionError(error));
      if (errorCallback) {
        errorCallback("An error occured while trying to save CFR form data");
      }
    });
};

export const saveCFRForm = (
  data,
  ministryId,
  requestId,
  isMinistry,
  dispatch,
  callback,
  errorCallback,
) => {
  if (!ministryId) {
    dispatch(serviceActionError("No request id"));
  }
  let baseUrl;
  if (isMinistry) {
    baseUrl = API.FOI_POST_CFR_FORM;
  } else {
    baseUrl = API.FOI_POST_CFR_FORM_IAO;
  }
  const apiUrl = replaceUrl(replaceUrl(
    baseUrl,
    "<requestid>",
    requestId
  ), "<ministryrequestid>", ministryId);
  console.log(`apiUrl == ${apiUrl}`)

  httpPOSTRequest(apiUrl, data)
    .then((res) => {
      if (res.data) {
        if (callback) {
          callback(res.data);
        }
        dispatch(fetchFOIRequestNotesList(requestId, ministryId));
      } else {
        dispatch(serviceActionError(res));
        throw new Error();
      }
    })
    .catch((error) => {
      console.log("An error occured while trying to save CFR form data", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to save CFR form data");
      }
    });
};

