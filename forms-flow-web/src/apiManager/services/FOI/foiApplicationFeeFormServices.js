import { httpGETRequest, httpPOSTRequest, httpPOSTRequestBlobResponse } from "../../httpRequestHandler";
  import UserService from "../../../services/UserService";
import API from "../../endpoints";
  import {
    serviceActionError,
    setRequestApplicationFeeForm
  } from "../../../actions/FOI/foiRequestActions";
  import { replaceUrl } from "../../../helper/FOI/helper";
  import { catchError } from "./foiServicesUtil";
  import _ from 'lodash';

export const fetchApplicationFeeForm = async (
  ministryId,
  requestId,
  dispatch,
  errorCallback = null
) => {
  if (ministryId == null || ministryId == undefined) {
    ministryId = 'None';
  }
  let apiUrl = replaceUrl(
      API.FOI_GET_APPLICATION_FEES_FORM,
      "<ministryrequestid>",
      ministryId
    )
  
  apiUrl = replaceUrl(apiUrl, "<requestid>", requestId);

  httpGETRequest(apiUrl, {}, UserService.getToken())
    .then((res) => {
      if (res.data) {
        dispatch(setRequestApplicationFeeForm(res.data));
      } else {
        console.log("Error in fetching fees data", res);
        dispatch(serviceActionError(res));
      }
    })
    .catch((error) => {
      console.log("Error in fetching fees data", error);
      dispatch(serviceActionError(error));
      if (errorCallback) {
        errorCallback("An error occured while trying to save fees form data");
      }
    });
};

export const saveApplicationFeeForm = (
  data,
  ministryId,
  requestId,
  dispatch,
  callback,
  errorCallback,
) => {
  let baseUrl = API.FOI_POST_APPLICATION_FEES_FORM;
  if (ministryId == null || ministryId == undefined) {
    ministryId = 'None';
  }
  const apiUrl = replaceUrl(replaceUrl(
    baseUrl,
    "<requestid>",
    requestId
  ), "<ministryrequestid>", ministryId);
  
  httpPOSTRequest(apiUrl, data)
    .then((res) => {
      if (res.data) {
        if (callback) {
          callback(res.data);
        }
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

export const generateReceiptFromOnlinePayment = (
  data,
  requestId,
  paymentId,
  dispatch,
  callback,
  errorCallback,
) => {
  let baseUrl = API.FOI_POST_RAWREQUEST_PAYMENT_RECEIPT;
  let apiUrl = replaceUrl(baseUrl, "<request_id>", requestId);
  apiUrl = replaceUrl(apiUrl, "<payment_id>", paymentId);
  
  httpPOSTRequestBlobResponse(apiUrl, data)
    .then((res) => {
      if (res.data) {
        if (callback) {
          callback(res.data);
        }
      } else {
        dispatch(serviceActionError(res));
        throw new Error();
      }
    })
    .catch((error) => {
      console.log("An error occured while trying to generate the application fee receipt", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to generate the application fee receipt");
      }
    });
};