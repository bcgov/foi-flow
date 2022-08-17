import { httpGETRequest, httpPOSTRequest } from "../../httpRequestHandler";
  import UserService from "../../../services/UserService";
import API from "../../endpoints/index";
  import {
    serviceActionError,
    setRequestFeeWaiverForm,
  } from "../../../actions/FOI/foiRequestActions";
  import { replaceUrl } from "../../../helper/FOI/helper";
  import { catchError } from "./foiServicesUtil";
  import { fetchFOIRequestNotesList } from "../../../apiManager/services/FOI/foiRequestNoteServices";
  import _ from 'lodash';

export const fetchFeeWaiverForm = (
  ministryId,
  dispatch,
  errorCallback = null
) => {
  const apiUrl = replaceUrl(
    API.FOI_GET_FEE_WAIVER_FORM,
    "<requestid>",
    ministryId
  );
  httpGETRequest(apiUrl, {}, UserService.getToken())
    .then((res) => {
      if (res.data) {
        if (!_.isEmpty(res.data)) {
          dispatch(setRequestFeeWaiverForm(res.data));
        }
      } else {
        console.log("Error in fetching Fee Waiver Form data", res);
        dispatch(serviceActionError(res));
      }
    })
    .catch((error) => {
      console.log("Error in fetching Fee Waiver Form data", error);
      dispatch(serviceActionError(error));
      if (errorCallback) {
        errorCallback("An error occured while trying to save Fee Waiver form data");
      }
    });
};


export const saveFeeWaiverForm = (
  FeeWaiverData,
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
    baseUrl = API.FOI_POST_FEE_WAIVER_FORM;
  } else {
    baseUrl = API.FOI_POST_FEE_WAIVER_FORM_IAO;
  }
  const apiUrl = replaceUrl(
    baseUrl,
    "<ministryrequestid>",
    ministryId
  );

  httpPOSTRequest(apiUrl, FeeWaiverData)
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
      console.log("An error occured while trying to save Fee Waiver form data", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to save Fee Waiver form data");
      }
    });
};