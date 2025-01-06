import {
    httpPOSTRequest,
    httpGETRequest,
    httpPUTRequest,
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
    setFOILoader,
    setRequestComments,
  } from "../../../actions/FOI/foiRequestActions";
  import UserService from "../../../services/UserService";
  import { replaceUrl, errorToast } from "../../../helper/FOI/helper";
  import { catchError } from './foiServicesUtil'

  export const fetchFOIRequestNotesList = (requestId, ministryId) => {
    let apiUrl = "";
    if (ministryId != null) {
      apiUrl = replaceUrl(
        API.FOI_GET_COMMENT_MINISTRYREQUEST,
        "<ministryrequestid>", ministryId);
  
    }
    else {
      apiUrl = replaceUrl(
        API.FOI_GET_COMMENT_RAWREQUEST,
        "<requestid>",
        requestId
      );
    }
    return (dispatch) => {
      httpGETRequest(apiUrl, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {           
            dispatch(setRequestComments(res.data));            
            dispatch(setFOILoader(false));
          } else {
            console.log("Error in fetching request notes", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          catchError(error, dispatch);
        });
    };
  };

  export const saveRawRequestNote = (data, requestid) => {    
    return (dispatch) => {
      httpPOSTRequest(API.FOI_POST_COMMENT_RAWREQUEST, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(requestid, null))
          if (res.data) {
            console.log("Saved request note successfully!");
          } else {
            dispatch(serviceActionError(res));
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
        });
    };
  };

  export const saveRequestHistoryComment = (data) => {    
    return async (dispatch) => {
      return httpPOSTRequest(API.FOI_POST_COMMENT_REQUESTHISTORY, data)
        .then((res) => {
          if (res.data) {
            console.log("Saved comment successfully!");
            return res.data
          } else {
            dispatch(serviceActionError(res));
          }
        })
        .catch((error) => {
          console.log(error, 'error')
          dispatch(serviceActionError(error));
        });
    };
  };
  
  export const saveMinistryRequestNote = (data,  ministryId) => {
    return (dispatch) => {
      httpPOSTRequest(API.FOI_POST_COMMENT_MINISTRYREQUEST, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(null, ministryId))
          if (res.data) {            
            console.log("Saved request note successfully!");
          } else {
            dispatch(serviceActionError(res));
            console.log("Error Posting Ministry Request Note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          console.log("Error Posting Ministry Request Note");
        });
    };
  };
  
  export const editRawRequestNote = (data, commentid, requestid) => {
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_PUT_COMMENT_RAWREQUEST,
    ), "<requestid>", commentid);
    return (dispatch) => {
      httpPUTRequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(requestid, null))
          if (res.data) {
            console.log("Edit raw request note successfully!")
          } else {
            dispatch(serviceActionError(res));
            console.log("Error editing raw request note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          console.log("Error editing raw request note");
        });
    };
  };
  export const editMinistryRequestNote = (data, commentid,  ministryId) => {
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_PUT_COMMENT_MINISTRYREQUEST,
    ), "<ministryrequestid>", commentid);    
    return (dispatch) => {
      httpPUTRequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(null, ministryId))
          if (res.data) {
            console.log("Edit ministry request note successfully!");
          } else {
            dispatch(serviceActionError(res));
            console.log("Error editing ministry request note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          console.log("Error editing ministry request note");
        });
    };
  };
    
  export const deleteRawRequestNote = (data, commentid,requestid) => {
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_DELETE_COMMENT_RAWREQUEST,
    ), "<commentid>", commentid);
    return (dispatch) => {
      httpPUTRequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(requestid, null))
          if (res.data.status) {
            console.log("Deleted raw request note successfully!");
          } else {
            dispatch(serviceActionError(res));
            errorToast(res.data.message)
            console.log("Error deleting Raw Request Note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          console.log("Error deleting Raw Request Note");
        });
    };
  };
  export const deleteMinistryRequestNote = (data, commentid,ministryId) => {
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_DELETE_COMMENT_MINISTRYREQUEST,
    ), "<commentid>", commentid);
    return (dispatch) => {
      httpPUTRequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(null, ministryId))
          if (res.data.status) {
            console.log("Deleted ministry request note successfully!");
          } else {
            dispatch(serviceActionError(res));
            errorToast(res.data.message)
            console.log(`Error deleting ministry Request Note with id ${commentid}`);
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          console.log(`Error deleting ministry Request Note with id ${commentid}`);
        });
    };
  };