import { httpPOSTRequest, httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  setFOIRequestList,
  serviceActionError,
  setFOIUpdateLoader,
  setFOILoader,
  setFOIRequestDetail,
  setFOICategoryList,
  setFOIProgramAreaList,
  clearRequestDetails,
  setFOIAssignedToList,
  setFOIDeliveryModeList,
  setFOIReceivedModeList,
} from "../../../actions/FOI/foiRequestActions";
import UserService from "../../../services/UserService";
import {replaceUrl} from "../../../helper/FOI/helper";

export const fetchFOICategoryList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const firstCategory = {"applicantcategoryid": 0, "name": "Select Category"};
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_CATEGORIES_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequestCategoryList = res.data;         
          let data = foiRequestCategoryList.map((category) => {
            return { ...category};
          });
          data.unshift(firstCategory);
          dispatch(setFOICategoryList(data));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIProgramAreaList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_PROGRAMAREAS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiProgramAreaList = res.data;         
          let data = foiProgramAreaList.map((programArea) => {
            return { ...programArea, isChecked: false};
          });
          dispatch(setFOIProgramAreaList(data));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};


export const fetchFOIAssignedToList = (requestType, status, ...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const unAssignedGroup = {"id":0,"name":"","members":[{"id": 0, "username": "Unassigned", "firstname":"", "lastname":""}]};
  let apiUrlGETAssignedToList = API.FOI_GET_ASSIGNEDTO_INTAKEGROUP_LIST_API;
  if (requestType && status) {
    apiUrlGETAssignedToList = replaceUrl(replaceUrl(
      API.FOI_GET_ASSIGNEDTOGROUPLIST_API,
      "<requesttype>",
      requestType
    ),"<curentstate>", status); 
  }  
  return (dispatch) => {
    httpGETRequest(apiUrlGETAssignedToList, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiAssignedToList = res.data;
          let data = foiAssignedToList.map((assignedTo) => {
            return { ...assignedTo};
          });
          data.unshift(unAssignedGroup);
          dispatch(setFOIAssignedToList(data));          
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIDeliveryModeList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const firstDeliveryMode = {"deliverymodeid": 0, "name": "Select Delivery Mode"};
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_DELIVERY_MODELIST, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiDeliveryModeList = res.data;                 
          let data = foiDeliveryModeList.map((deliveryMode) => {
            return { ...deliveryMode};
          });
          data.unshift(firstDeliveryMode);
          dispatch(setFOIDeliveryModeList(data));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIReceivedModeList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const firstReceivedMode = {"receivedmodeid": 0, "name": "Select Received Mode"};
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_RECEIVED_MODELIST, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiReceivedModeList = res.data;
          let data = foiReceivedModeList.map((receivedMode) => {
            return { ...receivedMode};
          });
          data.unshift(firstReceivedMode);
        
          dispatch(setFOIReceivedModeList(data));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIRequestList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_REQUESTS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequests = res.data;         
          let data = foiRequests.map((foiRequest) => {
            return { ...foiRequest};
          });
          dispatch(clearRequestDetails({}));
          dispatch(setFOIRequestList(data));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};

export const fetchFOIRawRequestDetails = (requestId,...rest) => {
  const done = rest.length ? rest[0] : () => {};
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
          dispatch(fetchFOIAssignedToList(foiRequest.requestType.toLowerCase(), foiRequest.currentState.replace(/\s/g, '').toLowerCase()));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));        
        done(error);
      });
  };
};

export const fetchFOIRequestDetails = (requestId, ministryId, ...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const apiUrlgetRequestDetails = replaceUrl(replaceUrl(
    API.FOI_REQUEST_API,
    "<requestid>",
    requestId
  ),"<ministryid>", ministryId);  
  return (dispatch) => {
    httpGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequest = res.data;         
          dispatch(clearRequestDetails({}));
          dispatch(setFOIRequestDetail(foiRequest));
          dispatch(fetchFOIAssignedToList(foiRequest.requestType.toLowerCase(), foiRequest.currentState.replace(/\s/g, '').toLowerCase()));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));        
        done(error);
      });
  };
};

export const saveRequestDetails = (data, urlIndexCreateRequest, requestId, ministryId, ...rest) => {
  const done = rest.length ? rest[0] : () => {};
  let id = urlIndexCreateRequest > -1? -1: requestId;
  let apiUrl = "";
  if (ministryId) {
    apiUrl = replaceUrl(replaceUrl(
      API.FOI_REQUEST_API,
      "<requestid>",
      requestId
    ),"<ministryid>", ministryId);  
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
          done("Error Posting data");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const openRequestDetails = (data, ...rest) => {  
  const done = rest.length ? rest[0] : () => {};
  return (dispatch) => {
    httpPOSTRequest(API.FOI_POST_REQUEST_POST, data)
      .then((res) => {
        if (res.data) {                   
          done(null, res.data);
        } else {         
          dispatch(serviceActionError(res));
          done("Error Posting data");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};