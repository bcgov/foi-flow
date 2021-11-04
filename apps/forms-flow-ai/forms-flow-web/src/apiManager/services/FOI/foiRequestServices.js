import { httpPOSTRequest, httpGETRequest, httpOSSPUTRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  setFOIRequestList,
  serviceActionError,
  setFOIUpdateLoader,
  setFOILoader,
  setFOIAssignedToListLoader,
  setFOIRequestDetail,
  setFOIMinistryViewRequestDetail,
  setFOICategoryList,
  setFOIProgramAreaList,
  clearRequestDetails,
  setFOIAssignedToList,
  setFOIFullAssignedToList,
  setFOIMinistryAssignedToList,
  setFOIDeliveryModeList,
  setFOIReceivedModeList,
  setFOIRequestDescriptionHistory,
  setFOIMinistryRequestList,
  setFOIMinistryDivisionalStages,
  clearFOIMinistryDivisionalStages,
  setFOIWatcherList,
  setClosingReasons
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


export const fetchFOIAssignedToList = (urlIndexCreateRequest, requestType, status, ...rest) => {
  const done = rest.length ? rest[0] : () => {};
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

export const fetchFOIFullAssignedToList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};

  return (dispatch) => {
    httpGETRequest(API.FOI_GET_ASSIGNEDTO_ALLGROUP_LIST_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiFullAssignedToList = res.data;
          let data = foiFullAssignedToList.map((assignedTo) => {
            return { ...assignedTo};
          });
          dispatch(setFOIFullAssignedToList(data));
          dispatch(setFOIAssignedToListLoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOIAssignedToListLoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOIAssignedToListLoader(false));
        done(error);
      });
  };
};

export const fetchFOIMinistryAssignedToList = (govCode, ...rest) => {
  const done = rest.length ? rest[0] : () => {};

  const apiUrlGETAssignedToList = replaceUrl(
    API.FOI_GET_ASSIGNEDTO_MINISTRYGROUP_LIST_API,
    "<govcode>",
    govCode
  );

  return (dispatch) => {
    httpGETRequest(apiUrlGETAssignedToList, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiAssignedToList = res.data;
          let data = foiAssignedToList.map((assignedTo) => {
            return { ...assignedTo};
          });
          dispatch(setFOIMinistryAssignedToList(data));          
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

export const fetchFOIWatcherList = (requestId, ministryId,...rest) => {
  const done = rest.length ? rest[0] : () => {};

  let apiUrl = '';
  if (ministryId) {
    apiUrl = replaceUrl(
      API.FOI_GET_MINISTRY_REQUEST_WATCHERS,
      "<ministryid>",
      ministryId
    );
  }
  else if (requestId) {
    apiUrl = replaceUrl(
      API.FOI_GET_RAW_REQUEST_WATCHERS,
      "<requestid>",
      requestId
    );
  }  
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          let data = res.data.map((watcher) => {
            return { ...watcher};
          });
          dispatch(setFOIWatcherList(data));
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

export const saveWatcher = (ministryId, data, ...rest) => {  
  const done = rest.length ? rest[0] : () => {};
  let apiUrl = API.FOI_POST_RAW_REQUEST_WATCHERS;
  if (ministryId) {
    apiUrl = API.FOI_POST_MINISTRY_REQUEST_WATCHERS;     
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
          // dispatch(setFOIAssignedToList([]));
          dispatch(fetchFOIAssignedToList(-1,"",""));
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

export const fetchFOIMinistryRequestList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_MINISTRY_REQUESTS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequests = res.data;         
          let data = foiRequests.map((foiRequest) => {
            foiRequest.bcgovcode = foiRequest.idNumber.split("-")[0];
            return { ...foiRequest};
          });          
          dispatch(clearRequestDetails({}));
          dispatch(fetchFOIMinistryAssignedToList(foiRequests[0].bcgovcode.toLowerCase()));     
          dispatch(setFOIMinistryRequestList(data));
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
          dispatch(setFOIAssignedToList([]));      
          dispatch(fetchFOIAssignedToList(-1,foiRequest.requestType.toLowerCase(), foiRequest.currentState.replace(/\s/g, '').toLowerCase()));
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
          //dispatch(setFOIAssignedToList([]));
          dispatch(fetchFOIAssignedToList(-1,foiRequest.requestType.toLowerCase(), foiRequest.currentState.replace(/\s/g, '').toLowerCase()));
          dispatch(fetchFOIMinistryAssignedToList(foiRequest.selectedMinistries[0].code.toLowerCase()));
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

export const fetchFOIMinistryViewRequestDetails = (requestId, ministryId, ...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const apiUrlgetRequestDetails = replaceUrl(replaceUrl(
    API.FOI_MINISTRYVIEW_REQUEST_API,
    "<requestid>",
    requestId
  ),"<ministryid>", ministryId);  
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

export const fetchFOIMinistryDivisionalStages = (bcgovcode, ...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const apiUrlgetdivisionalstages = replaceUrl(API.FOI_MINISTRY_DIVISIONALSTAGES,"<bcgovcode>", bcgovcode);  
  return (dispatch) => {
    httpGETRequest(apiUrlgetdivisionalstages, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiMinistryDivisionalStages = res.data;         
          dispatch(clearFOIMinistryDivisionalStages({}));
          dispatch(setFOIMinistryDivisionalStages(foiMinistryDivisionalStages));                             
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

export const saveMinistryRequestDetails = (data, requestId, ministryId, ...rest) => {  
  const done = rest.length ? rest[0] : () => {};
  let apiUrl = "";
  if (ministryId) {
    apiUrl = replaceUrl(replaceUrl(
      API.FOI_MINISTRYVIEW_REQUEST_API,
      "<requestid>",
      requestId
    ),"<ministryid>", ministryId);  
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
  }
  done("Error Posting data");
};

export const fetchFOIRequestDescriptionList = (requestId, ministryId,...rest) => {
  const done = rest.length ? rest[0] : () => {};  
  let apiUrl = "";
  if (ministryId) {
    apiUrl = replaceUrl(replaceUrl(
      API.FOI_MINISTRY_REQUEST_DESCRIPTION,     
    ),"<ministryid>", ministryId);  
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

export const fetchClosingReasonList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_CLOSING_REASONS, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const closingReasons = res.data;
          dispatch(setClosingReasons(closingReasons));
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

export const getOSSHeaderDetails = (data, ...rest) => {  
  const done = rest.length ? rest[0] : () => {};  
    return (dispatch) => {
      httpPOSTRequest(API.FOI_POST_OSS_HEADER, data)
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

export const saveFilesinS3 = (headerDetails, file, ...rest) => {  
  const done = rest.length ? rest[0] : () => {};
  var requestOptions = {
    headers: {
      'X-Amz-Date': headerDetails.amzdate,
      'Authorization': headerDetails.authheader,     
    }    
  };  
    return (dispatch) => {
      httpOSSPUTRequest(headerDetails.filepath, file, requestOptions)
        .then((res) => {
          if (res) {
            done(null, res.status);
          } else {
            dispatch(serviceActionError(res));
            done("Error");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done(error);
        });
    };
};
