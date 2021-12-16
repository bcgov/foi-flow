import {
  httpPOSTRequest,
  httpGETRequest,
} from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  setFOIRequestList,
  serviceActionError,
  setFOILoader,
  setFOIRequestDetail,
  setFOIMinistryViewRequestDetail,
  clearRequestDetails,
  setFOIAssignedToList,
  setFOIRequestDescriptionHistory,
  setFOIMinistryRequestList,
} from "../../../actions/FOI/foiRequestActions";
import { fetchFOIAssignedToList, fetchFOIMinistryAssignedToList } from "./foiMasterDataServices";
import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper"; 

export const fetchFOIRequestList = (...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_REQUESTS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequests = res.data;
          let data = foiRequests.map((foiRequest) => {
            return { ...foiRequest };
          });
          dispatch(clearRequestDetails({}));
          dispatch(fetchFOIAssignedToList("", ""));
          dispatch(setFOIRequestList(data));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error in fetching dashboard data for IAO", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error in fetching dashboard data for IAO", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIMinistryRequestList = (...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_MINISTRY_REQUESTS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequests = res.data;
          let data = foiRequests.map((foiRequest) => {
            foiRequest.bcgovcode = foiRequest.idNumber.split("-")[0];
            return { ...foiRequest };
          });
          dispatch(clearRequestDetails({}));
          if (foiRequests > 0)
            dispatch(fetchFOIMinistryAssignedToList( foiRequests[0].bcgovcode.toLowerCase()));     
          dispatch(setFOIMinistryRequestList(data));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error in fetching dashboard data for Ministry", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error in fetching dashboard data for Ministry", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIRawRequestDetails = (requestId, ...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  const apiUrlgetRequestDetails = replaceUrl(
    API.FOI_RAW_REQUEST_API,
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequest = res.data;
          dispatch(clearRequestDetails({}));
          dispatch(setFOIRequestDetail(foiRequest));
          dispatch(setFOIAssignedToList([]));
          dispatch(fetchFOIAssignedToList(foiRequest.requestType.toLowerCase(), foiRequest.currentState.replace(/\s/g, '').toLowerCase()));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log(`Error in fetching raw request details for request# ${requestId}`, res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log(`Error in fetching raw request details for request# ${requestId}`, error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIRequestDetails = (requestId, ministryId, ...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  const apiUrlgetRequestDetails = replaceUrl(replaceUrl(
    API.FOI_REQUEST_API,
    "<requestid>",
    requestId
  ), "<ministryid>", ministryId);
  return (dispatch) => {
    httpGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequest = res.data;
          dispatch(clearRequestDetails({}));
          dispatch(setFOIRequestDetail(foiRequest));
          dispatch(fetchFOIAssignedToList(foiRequest.requestType.toLowerCase(), foiRequest.currentState.replace(/\s/g, '').toLowerCase()));
          dispatch(fetchFOIMinistryAssignedToList(foiRequest.selectedMinistries[0].code.toLowerCase()));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log(`Error in fetching request details for request# ${requestId} ministry# ${ministryId}`, res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log(`Error in fetching request details for request# ${requestId} ministry# ${ministryId}`, error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIMinistryViewRequestDetails = (requestId, ministryId, ...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  const apiUrlgetRequestDetails = replaceUrl(replaceUrl(
    API.FOI_MINISTRYVIEW_REQUEST_API,
    "<requestid>",
    requestId
  ), "<ministryid>", ministryId);
  return (dispatch) => {
    httpGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequest = res.data;
          dispatch(clearRequestDetails({}));
          dispatch(setFOIMinistryViewRequestDetail(foiRequest));
          dispatch(fetchFOIMinistryAssignedToList(foiRequest.selectedMinistries[0].code.toLowerCase()));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log(`Error in fetching ministry request details for request# ${requestId} ministry# ${ministryId}`, res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log(`Error in fetching ministry request details for request# ${requestId} ministry# ${ministryId}`, error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const saveRequestDetails = (data, urlIndexCreateRequest, requestId, ministryId, ...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  let id = urlIndexCreateRequest > -1 ? -1 : requestId;
  let apiUrl = "";
  if (ministryId) {
    apiUrl = replaceUrl(replaceUrl(
      API.FOI_REQUEST_API,
      "<requestid>",
      requestId
    ), "<ministryid>", ministryId);
  }
  else {
    apiUrl = replaceUrl(
      API.FOI_RAW_REQUEST_API,
      "<requestid>",
      id
    );
  }
  return (dispatch) => {
    httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          done(`Error in saving request details for the request# ${requestId} and ministry# ${ministryId}`);
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(`Error in saving request details for the request# ${requestId} and ministry# ${ministryId}`);
      });
  };
};

export const openRequestDetails = (data, ...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  return (dispatch) => {
    httpPOSTRequest(API.FOI_POST_REQUEST_POST, data)
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          done(`Error while opening the request`);
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(`Error while opening the request`);
      });
  };
};

export const saveMinistryRequestDetails = (data, requestId, ministryId, ...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  let apiUrl = "";
  if (ministryId) {
    apiUrl = replaceUrl(replaceUrl(
      API.FOI_MINISTRYVIEW_REQUEST_API,
      "<requestid>",
      requestId
    ), "<ministryid>", ministryId);
    return (dispatch) => {
      httpPOSTRequest(apiUrl, data)
        .then((res) => {
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            done(`Error while saving the ministry request (request# ${requestId}, ministry# ${ministryId})`);
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done(`Error while saving the ministry request (request# ${requestId}, ministry# ${ministryId})`);
        });
    };
  }
  done("Error Posting data");
};

export const fetchFOIRequestDescriptionList = (requestId, ministryId, ...rest) => {
  const done = rest.length ? rest[0] : () => {
      //This is intentional
   };
  let apiUrl = "";
  if (ministryId) {
    apiUrl = replaceUrl(replaceUrl(
      API.FOI_MINISTRY_REQUEST_DESCRIPTION,
    ), "<ministryid>", ministryId);
  }
  else {
    apiUrl = replaceUrl(
      API.FOI_RAW_REQUEST_DESCRIPTION,
      "<requestid>",
      requestId
    );
  }
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setFOIRequestDescriptionHistory(res.data.audit));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          done(`Error while fetching the request description history (request# ${requestId}, ministry# ${ministryId})`);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(`Error while fetching the request description history (request# ${requestId}, ministry# ${ministryId})`);
      });
  };
};