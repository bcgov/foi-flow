import {
    httpPOSTRequest,
    httpGETRequest,
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
    setFOIAttachmentListLoader,
    setRawRequestAttachments,
    setMinistryRequestAttachments
  } from "../../../actions/FOI/foiRequestActions";
  import UserService from "../../../services/UserService";
  import { replaceUrl } from "../../../helper/FOI/helper";

 export const fetchFOIRequestAttachmentsList = (requestId, ministryId, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    let apiUrl = "";
    if (ministryId !=null) {
      apiUrl = replaceUrl(
        API.FOI_ATTACHMENTS_MINISTRYREQUEST,
       "<ministryrequestid>", ministryId);
    }
    else {
      apiUrl = replaceUrl(
        API.FOI_ATTACHMENTS_RAWREQUEST,
        "<requestid>",
        requestId
      );
    }
    return (dispatch) => {
      httpGETRequest(apiUrl, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            if (ministryId!=null) {
              dispatch(setMinistryRequestAttachments(res.data));
            }
  
            if (requestId) {
              dispatch(setRawRequestAttachments(res.data));
            }
  
            dispatch(setFOIAttachmentListLoader(false));
            done(null, res.data);
            
          } else {
            console.log("Error in fetching attachment list", res);
            dispatch(serviceActionError(res));
            dispatch(setFOIAttachmentListLoader(false));
          }
        })
        .catch((error) => {
          console.log("Error in fetching attachment list", error);
          dispatch(serviceActionError(error));
          dispatch(setFOIAttachmentListLoader(false));
          done(error);
        });
    };
  };

  export const saveFOIRequestAttachmentsList = (requestId, ministryId, data, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    let apiUrl = "";
    if (ministryId !=null) {
      apiUrl = replaceUrl(
        API.FOI_ATTACHMENTS_MINISTRYREQUEST,
       "<ministryrequestid>", ministryId);
    }
    else {
      apiUrl = replaceUrl(
        API.FOI_ATTACHMENTS_RAWREQUEST,
        "<requestid>",
        requestId
      );
    }
    return (dispatch) => {
      httpPOSTRequest(apiUrl, data)
        .then((res) => {          
          if (res.data) {
            dispatch(fetchFOIRequestAttachmentsList(requestId,ministryId));
            dispatch(setFOIAttachmentListLoader(false));           
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            dispatch(setFOIAttachmentListLoader(false));
            done("Error in posting Attachments");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          dispatch(setFOIAttachmentListLoader(false));
          done("Error in posting Attachments");
        });
    };
  };

  export const saveNewFilename = (newFilename, documentId, requestId, ministryId, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };

    let apiUrl = "";
    if (ministryId !=null) {
      apiUrl = replaceUrl(
        API.FOI_RENAME_ATTACHMENTS_MINISTRYREQUEST+'',
       "<ministryrequestid>", ministryId);
    }
    else {
      apiUrl = replaceUrl(
        API.FOI_RENAME_ATTACHMENTS_RAWREQUEST,
        "<requestid>",
        requestId
      );
    }
    apiUrl = replaceUrl(
      apiUrl,
      "<documentid>",
      documentId
    );

    return (dispatch) => {
      const data = {
        filename: newFilename
      };
      httpPOSTRequest(apiUrl, data)
        .then((res) => {          
          if (res.data) {
            dispatch(fetchFOIRequestAttachmentsList(requestId,ministryId));
            dispatch(setFOIAttachmentListLoader(false));           
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            dispatch(setFOIAttachmentListLoader(false));
            done("Error in renaming the file");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          dispatch(setFOIAttachmentListLoader(false));
          done("Error in renaming the file");
        });
    };
  };

  export const replaceFOIRequestAttachment = (requestId, ministryId, documentId, data, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    let apiUrl = "";

    if (ministryId && documentId) {
      apiUrl = replaceUrl(replaceUrl(
        API.FOI_REPLACE_ATTACHMENT_MINISTRYREQUEST,
        "<ministryrequestid>",
        ministryId
      ), "<documentid>", documentId);
    } else {
      apiUrl = replaceUrl(replaceUrl(
        API.FOI_REPLACE_ATTACHMENT_RAWREQUEST,
        "<requestid>",
        requestId
      ), "<documentid>", documentId);      
    }
    return (dispatch) => {
      httpPOSTRequest(apiUrl, data)
        .then((res) => {          
          if (res.data) {
            dispatch(fetchFOIRequestAttachmentsList(requestId,ministryId));
            dispatch(setFOIAttachmentListLoader(false));           
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            dispatch(setFOIAttachmentListLoader(false));
            done("Error in replacing the attachment");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          dispatch(setFOIAttachmentListLoader(false));
          done("Error in replacing the attachment");
        });
    };
  };

  export const deleteFOIRequestAttachment = (requestId, ministryId, documentId, data, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    let apiUrl = "";

    if (ministryId && documentId) {
      apiUrl = replaceUrl(replaceUrl(
        API.FOI_DELETE_ATTACHMENT_MINISTRYREQUEST,
        "<ministryrequestid>",
        ministryId
      ), "<documentid>", documentId);
    } else {
      apiUrl = replaceUrl(replaceUrl(
        API.FOI_DELETE_ATTACHMENT_RAWREQUEST,
        "<requestid>",
        requestId
      ), "<documentid>", documentId);      
    }
    return (dispatch) => {
      httpPOSTRequest(apiUrl, data)
        .then((res) => {
          if (res.data) {
            dispatch(fetchFOIRequestAttachmentsList(requestId,ministryId));
            dispatch(setFOIAttachmentListLoader(false));           
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            dispatch(setFOIAttachmentListLoader(false));
            done("Error in deleting an attachment");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          dispatch(setFOIAttachmentListLoader(false));
          done("Error in deleting an attachment");
        });
    };
  };