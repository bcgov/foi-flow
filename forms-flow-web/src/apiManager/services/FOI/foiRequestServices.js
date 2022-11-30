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
  clearMinistryViewRequestDetails,
  setFOIRequestDescriptionHistory,
  setFOIMinistryRequestList,
  setOpenedMinistries,
} from "../../../actions/FOI/foiRequestActions";
import { fetchFOIAssignedToList, fetchFOIMinistryAssignedToList, fetchFOIProcessingTeamList } from "./foiMasterDataServices";
import { catchError, fnDone} from './foiServicesUtil';
import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper";
import { persistRequestFieldsNotInAxis } from "../../../components/FOI/FOIRequest/utils";

export const fetchFOIRequestList = () => {
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_REQUESTS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequests = res.data;
          let data = foiRequests.map((foiRequest) => {
            return { ...foiRequest };
          });
          dispatch(clearRequestDetails({}));
          dispatch(setFOIRequestList(data));
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error in fetching dashboard data for IAO");
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};

export const fetchFOIRequestListByPage = (
  page = 1,
  size = 10,
  sort = [{ field: "defaultSorting", sort: "asc" }],
  filters = null,
  keyword = null,
  additionalFilter = "All",
  userID = null
) => {
  let sortingItems = [];
  let sortingOrders = [];
  sort.forEach((item) => {
    sortingItems.push(item.field);
    sortingOrders.push(item.sort);
  });

  return (dispatch) => {
    dispatch(setFOILoader(true));
    httpGETRequest(
      API.FOI_GET_REQUESTS_PAGE_API,
      {
        page: page,
        size: size,
        sortingitems: sortingItems,
        sortingorders: sortingOrders,
        filters: filters,
        keyword: keyword,
        additionalfilter: additionalFilter,
        userid: userID,
      },
      UserService.getToken()
    )
      .then((res) => {
        if (res.data) {
          dispatch(clearRequestDetails({}));
          dispatch(setFOIRequestList(res.data));
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error in fetching dashboard data for IAO");
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};

export const fetchFOIMinistryRequestList = () => {
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_MINISTRY_REQUESTS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequests = res.data;
          let data = foiRequests.map((foiRequest) => {
            foiRequest.bcgovcode = foiRequest.idNumber.split("-")[0];
            return { ...foiRequest };
          });
          dispatch(clearMinistryViewRequestDetails({}));
          if (foiRequests > 0)
            dispatch(fetchFOIMinistryAssignedToList( foiRequests[0].bcgovcode.toLowerCase()));     
          dispatch(setFOIMinistryRequestList(data));
          dispatch(setFOILoader(false));
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error in fetching dashboard data for Ministry");
        }
      })
      .catch((error) => {        
        catchError(error, dispatch);
      });
  };
};

export const fetchFOIMinistryRequestListByPage = (page = 1, size = 10, sort = [{field:'defaultSorting', sort:'asc'}], filters = null, keyword = null, additionalFilter = 'All', userID = null) => {
  let sortingItems = [];
  let sortingOrders = [];
  sort.forEach((item)=>{
    sortingItems.push(item.field);
    sortingOrders.push(item.sort);
  });

  return (dispatch) => {
    httpGETRequest(
          API.FOI_GET_MINISTRY_REQUESTS_PAGE_API,
          {
            "page": page,
            "size": size,
            "sortingitems": sortingItems,
            "sortingorders": sortingOrders,
            "filters": filters,
            "keyword": keyword,
            "additionalfilter": additionalFilter,
            "userid": userID
          },
          UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(clearMinistryViewRequestDetails({}));
          dispatch(setFOIMinistryRequestList(res.data));
          dispatch(setFOILoader(false));
          if (res.data?.data[0]?.bcgovcode)
            dispatch(fetchFOIMinistryAssignedToList(res.data.data[0].bcgovcode));     
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error in fetching dashboard data for IAO");
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};

export const fetchFOIRequestDetailsWrapper = (requestId, ministryId) => {
  if (ministryId) {
    return fetchFOIRequestDetails(requestId, ministryId);
  } else {
    return fetchFOIRawRequestDetails(requestId);
  }
};

export const fetchFOIRawRequestDetails = (requestId) => {
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
          dispatch(fetchFOIAssignedToList(foiRequest.requestType.toLowerCase(), foiRequest.currentState.replace(/\s/g, '').toLowerCase(), ""));
          dispatch(fetchFOIProcessingTeamList(foiRequest.requestType.toLowerCase()));
          dispatch(setFOILoader(false));
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error in fetching raw request details for request# ${requestId}`);
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  }
};

export const fetchFOIRequestDetails = (requestId, ministryId) => {
  
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
          const ministryCode = foiRequest.selectedMinistries[0].code.toLowerCase();
          dispatch(fetchFOIAssignedToList(foiRequest.requestType.toLowerCase(), foiRequest.currentState.replace(/\s/g, '').toLowerCase(), ministryCode));
          dispatch(fetchFOIMinistryAssignedToList(ministryCode));
          dispatch(fetchFOIProcessingTeamList(foiRequest.requestType.toLowerCase()));
          dispatch(setFOILoader(false));
        } else {
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
          throw new Error(`Error in fetching request details for request# ${requestId} ministry# ${ministryId}`)
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};

export const fetchFOIMinistryViewRequestDetails = (requestId, ministryId) => {
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
          dispatch(clearMinistryViewRequestDetails({}));
          dispatch(setFOIMinistryViewRequestDetail(foiRequest));
          dispatch(fetchFOIMinistryAssignedToList(foiRequest.selectedMinistries[0].code.toLowerCase()));
          dispatch(setFOILoader(false));
        } else {
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
          throw new Error(`Error in fetching ministry request details for request# ${requestId} ministry# ${ministryId}`)
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};

export const saveRequestDetails = (data, urlIndexCreateRequest, requestId, ministryId, ...rest) => {
  const done = fnDone(rest);
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
          throw new Error(`Error in saving request details for the request# ${requestId} and ministry# ${ministryId}`);
        }
      })
      .catch((error) => {
        done(error);
        catchError(error, dispatch);
      });
  };
};

export const openRequestDetails = (data, ...rest) => {
  const done = fnDone(rest);
  return (dispatch) => {
    httpPOSTRequest(API.FOI_POST_REQUEST_POST, data)
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error while opening the request");
        }
      })
      .catch((error) => {
        done(error);
        catchError(error, dispatch);
      });
  };
};

export const saveMinistryRequestDetails = (data, requestId, ministryId, ...rest) => {
  const done = fnDone(rest);
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
            throw new Error(`Error while saving the ministry request (request# ${requestId}, ministry# ${ministryId})`);            
          }
        })
        .catch((error) => {
          done(error);
          catchError(error, dispatch);
        });
    };
  }
};

export const fetchFOIRequestDescriptionList = (requestId, ministryId) => {
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
        } else {
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
          throw new Error(`Error while fetching the request description history (request# ${requestId}, ministry# ${ministryId})`);
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};

export const fetchOpenedMinistriesForNotification = (notification, ...rest) => {
  const done = fnDone(rest);
  const apiUrlgetRequestDetails = replaceUrl(
    API.FOI_GET_OPENED_MINISTRIES,
    "<requestid>",
    notification.requestid,
    "<names>",
    "ministries"
  );
  return (dispatch) => {
    httpGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setOpenedMinistries(res.data));
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error in fetching raw request details for request# ${notification.requestId}`);
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  }
};

export const checkDuplicateAndFetchRequestDataFromAxis = (axisRequestId, isModal,requestDetails, ...rest) => {
  const done = fnDone(rest);
  const apiUrlCheckAxisIdExists = replaceUrl(
    API.FOI_CHECK_AXIS_REQUEST_ID,
    "<axisrequestid>",
    axisRequestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrlCheckAxisIdExists, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          if(!res.data.ispresent){
            dispatch(fetchRequestDataFromAxis(axisRequestId, isModal,requestDetails,(err, data) => {
              if(!err)
                done(null, data);
              else {
                  done(null,"Exception happened while fetching request from AXIS.");
                  dispatch(serviceActionError(res));
                  throw new Error(`Error in fetching request from AXIS.`);
              }
            }));
          }
          else
            done(null,"Axis Id exists");
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error in fetching axis request ids.`);
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  }
};

export const fetchRequestDataFromAxis = (axisRequestId, isModal,requestDetails, ...rest) => {
  const done = fnDone(rest);
  const apiUrlgetRequestDetails = replaceUrl(
    API.FOI_GET_AXIS_REQUEST_DATA,
    "<axisrequestid>",
    axisRequestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          let newRequest = res.data;
          if(!isModal && Object.entries(newRequest).length !== 0){
            if(Object.entries(requestDetails).length !== 0 && requestDetails.currentState === "Unopened"){
              newRequest= persistRequestFieldsNotInAxis(newRequest,requestDetails);
            }
            dispatch(setFOIRequestDetail(newRequest));
          }
          done(null, newRequest);
        } else {
          done(null,"Exception happened while GET operations of request");
          dispatch(serviceActionError(res));
          throw new Error(`Error in fetching request from AXIS.`);
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
        done(null,"Exception happened while GET operations of request");
      });
  }
};

