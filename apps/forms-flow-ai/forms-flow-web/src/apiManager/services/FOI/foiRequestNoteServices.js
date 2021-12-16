import {
    httpPOSTRequest,
    httpGETRequest,
    httpPUTRequest,
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
    setFOILoader,
    setRawRequestComments,
    setMinistryRequestComments,
  } from "../../../actions/FOI/foiRequestActions";
  import UserService from "../../../services/UserService";
  import { replaceUrl } from "../../../helper/FOI/helper";

  export const fetchFOIRequestNotesList = (requestId, ministryId, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
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
            if (ministryId != null) {
              dispatch(setMinistryRequestComments(res.data));
            }
            if (requestId != null) {
              dispatch(setRawRequestComments(res.data));
            }  
            dispatch(setFOILoader(false));
            done(null, res.data);  
          } else {
            console.log("Error in fetching request notes", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error in fetching request notes", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
          done(error);
        });
    };
  };

  export const saveRawRequestNote = (data, requestid, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    return (dispatch) => {
      httpPOSTRequest(API.FOI_POST_COMMENT_RAWREQUEST, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(requestid, null))
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            done("Error Posting Raw Request Note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done("Error Posting Raw Request Note");
        });
    };
  };
  export const saveMinistryRequestNote = (data,  ministryId, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    return (dispatch) => {
      httpPOSTRequest(API.FOI_POST_COMMENT_MINISTRYREQUEST, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(null, ministryId))
          if (res.data) {            
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            done("Error Posting Ministry Request Note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done("Error Posting Ministry Request Note");
        });
    };
  };
  
  export const editRawRequestNote = (data, commentid, requestid, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_PUT_COMMENT_RAWREQUEST,
    ), "<requestid>", commentid);
    return (dispatch) => {
      httpPUTRequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(requestid, null))
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            done("Error editing raw request note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done("Error editing raw request note");
        });
    };
  };
  export const editMinistryRequestNote = (data, commentid,  ministryId, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_PUT_COMMENT_MINISTRYREQUEST,
    ), "<ministryrequestid>", commentid);    
    return (dispatch) => {
      httpPUTRequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(null, ministryId))
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            done("Error editing ministry request note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done("Error editing ministry request note");
        });
    };
  };
    
  export const deleteRawRequestNote = (data, commentid,requestid, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_DELETE_COMMENT_RAWREQUEST,
    ), "<commentid>", commentid);
    return (dispatch) => {
      httpPUTRequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(requestid, null))
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            done("Error deleting Raw Request Note");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done("Error deleting Raw Request Note");
        });
    };
  };
  export const deleteMinistryRequestNote = (data, commentid,ministryId, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_DELETE_COMMENT_MINISTRYREQUEST,
    ), "<commentid>", commentid);
    return (dispatch) => {
      httpPUTRequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOIRequestNotesList(null, ministryId))
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            done(`Error deleting ministry Request Note with id ${commentid}`);
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done(`Error deleting ministry Request Note with id ${commentid}`);
        });
    };
  };