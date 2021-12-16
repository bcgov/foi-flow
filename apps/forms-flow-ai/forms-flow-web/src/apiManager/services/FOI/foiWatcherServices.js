import {
    httpPOSTRequest,
    httpGETRequest,
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
    setFOILoader,
    setFOIWatcherList,
  } from "../../../actions/FOI/foiRequestActions";
  import UserService from "../../../services/UserService";
  import { replaceUrl } from "../../../helper/FOI/helper";

export const fetchFOIWatcherList = (requestId, ministryId, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
  
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
              return { ...watcher };
            });
            dispatch(setFOIWatcherList(data));
            dispatch(setFOILoader(false));
            done(null, res.data);
          } else {
            console.log("Error in fetching watcher list", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error in fetching watcher list", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
          done(error);
        });
    };
  };
  
  export const saveWatcher = (ministryId, data, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
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
            done("Error in updating watcher list");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done("Error in updating watcher list");
        });
    };
  };