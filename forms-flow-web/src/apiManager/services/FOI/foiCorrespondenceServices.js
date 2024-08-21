import { httpGETRequest, httpPOSTRequest } from "../../httpRequestHandler";
  import UserService from "../../../services/UserService";
import API from "../../endpoints";
  import {
    serviceActionError,
    setApplicantCorrespondence,
    setApplicantCorrespondenceTemplates,
    setFOICorrespondenceLoader
  } from "../../../actions/FOI/foiRequestActions";
  import { replaceUrl } from "../../../helper/FOI/helper";
  import { catchError } from "./foiServicesUtil";
  import _ from 'lodash';

export const fetchApplicantCorrespondence = (
  requestId,
  ministryId,
  errorCallback = null
) => {

  if (ministryId == null) {
    ministryId = 'None'
  }
  const apiUrl = replaceUrl(replaceUrl(
    API.FOI_GET_EMAIL_CORRESPONDENCE,
    "<ministryrequestid>",
    ministryId),"<requestid>",requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setApplicantCorrespondence(res.data));
        } else {
          console.log("Error in fetching Applicant Correspondence data", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        console.log("Error in fetching Applicant Correspondence data", error);
        dispatch(serviceActionError(error));
        if (errorCallback) {
          errorCallback("An error occured while trying to save Applicant Correspondence data");
        }
      });
      dispatch(setFOICorrespondenceLoader(false));
    };
};

export const saveEmailCorrespondence = (
  data,
  requestId,
  ministryId,
  dispatch,
  callback,
  errorCallback,
) => {
  if (!ministryId) {
    ministryId = 'None';
  }
  dispatch(setFOICorrespondenceLoader(true));
  const apiUrl = replaceUrl(replaceUrl(
    API.FOI_POST_EMAIL_CORRESPONDENCE,
    "<ministryrequestid>",
    ministryId),"<requestid>",requestId
  );
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
      console.log("An error occured while trying to send email to applicant", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to send email to applicant");
      }
    });
};

export const saveDraftCorrespondence = (
  data,
  requestId,
  ministryId,
  dispatch,
  callback,
  errorCallback,
) => {
  if (!ministryId) {
    ministryId = 'None';
  }
  dispatch(setFOICorrespondenceLoader(true));
  const apiUrl = replaceUrl(replaceUrl(
    API.FOI_POST_DRAFT_EMAIL_CORRESPONDENCE,
    "<ministryrequestid>",
    ministryId),"<requestid>",requestId
  );
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
      console.log("An error occured while trying to send email to applicant", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to send email to applicant");
      }
    });
};


export const editDraftCorrespondence = (
  data,
  requestId,
  ministryId,
  dispatch,
  callback,
  errorCallback,
) => {
  if (!ministryId) {
    ministryId = 'None';
  }
  dispatch(setFOICorrespondenceLoader(true));
  const apiUrl = replaceUrl(replaceUrl(
    API.FOI_EDIT_DRAFT_EMAIL_CORRESPONDENCE,
    "<ministryrequestid>",
    ministryId),"<requestid>",requestId
  );
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
      console.log("An error occured while trying to send email to applicant", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to send email to applicant");
      }
    });
};

export const deleteDraftCorrespondence = (
  correspondenceid,
  ministryId,
  requestId,
  dispatch,
  callback,
  errorCallback,
) => {
  if (!ministryId) {
    ministryId = 'None';
  }
  dispatch(setFOICorrespondenceLoader(true));
  let apiUrl = replaceUrl(replaceUrl(
    API.FOI_DELETE_DRAFT_EMAIL_CORRESPONDENCE,
    "<ministryrequestid>",
    ministryId),"<correspondenceid>", correspondenceid,

  );
  apiUrl = replaceUrl(apiUrl,"<rawrequestid>",requestId);
  httpPOSTRequest(apiUrl,{})
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
      console.log("An error occured while trying to send email to applicant", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to send email to applicant");
      }
    });
};

export const deleteResponseCorrespondence = (
  correspondenceid,
  ministryId,
  requestId,
  dispatch,
  callback,
  errorCallback,
) => {
  if (!ministryId) {
    ministryId = 'None';
  }
  dispatch(setFOICorrespondenceLoader(true));
  let apiUrl = replaceUrl(replaceUrl(
    API.FOI_DELETE_RESPONSE_EMAIL_CORRESPONDENCE,
    "<ministryrequestid>",
    ministryId),"<correspondenceid>", correspondenceid,

  );
  apiUrl = replaceUrl(apiUrl,"<rawrequestid>",requestId);
  httpPOSTRequest(apiUrl,{})
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
      console.log("An error occured while trying to delete the response correspondence", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to delete the response correspondence");
      }
    });
};

export const saveCorrespondenceResponse = (
  data,
  ministryId,
  requestId,
  dispatch,
  callback,
  errorCallback,
) => {
  if (!ministryId) {
    ministryId = 'None';
  }
  dispatch(setFOICorrespondenceLoader(true));
  const apiUrl = replaceUrl(replaceUrl(
    API.FOI_POST_RESPONSE_EMAIL_CORRESPONDENCE,
    "<ministryrequestid>",
    ministryId), 
    "<rawrequestid>", requestId);
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
      console.log("An error occured while trying to save response from applicant", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to save response from applicant");
      }
    });
};

export const editCorrespondenceResponse = (
  data,
  ministryId,
  rawRequestId,
  dispatch,
  callback,
  errorCallback,
) => {
  if (!ministryId) {
    ministryId = 'None';
  }
  dispatch(setFOICorrespondenceLoader(true));
  const apiUrl = replaceUrl(replaceUrl(
    API.FOI_EDIT_RESPONSE_EMAIL_CORRESPONDENCE,
    "<ministryrequestid>",
    ministryId), 
    "<rawrequestid>", rawRequestId
  );
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
      console.log("An error occured while trying to save response from applicant", error);
      catchError(error, dispatch);
      if (errorCallback) {
        errorCallback("An error occured while trying to save response from applicant");
      }
    });
};

export const fetchApplicantCorrespondenceTemplates = (
  errorCallback = null
) => {
  const apiUrl = API.FOI_GET_EMAIL_CORRESPONDENCE_TEMPLATES;
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          if (!_.isEmpty(res.data)) {
            dispatch(setApplicantCorrespondenceTemplates(res.data));
          }
        } else {
          console.log("Error in fetching Applicant Correspondence templates", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        console.log("Error in fetching Applicant Correspondence templates", error);
        dispatch(serviceActionError(error));
        if (errorCallback) {
          errorCallback("An error occured while trying to fetch Applicant Correspondence templates");
        }
      });
    };
};