import { httpPOSTRequest, httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  serviceActionError,
  setFOILoader,
  setFOIOpenInfoRequest,
  setFOIOpenInfoAdditionalFiles,
  setFOIRequestDetail
} from "../../../actions/FOI/foiRequestActions";
import { fnDone, catchError } from "./foiServicesUtil";
import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper";
import { OIStates, OIPublicationStatuses, OIExemptions } from "../../../helper/openinfo-helper";

export const fetchFOIOpenInfoRequest = (foiministryrequestid) => {
  if (!foiministryrequestid) {
    return () => {};
  }
  const foiOpenInfoRequestAPIUrl = replaceUrl(
    replaceUrl(API.FOI_GET_OPENINFO_REQUEST),
    "<ministryrequestid>",
    foiministryrequestid
  );
  return (dispatch) => {
    httpGETRequest(foiOpenInfoRequestAPIUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiOpenInfoRequest = res.data;
          dispatch(setFOIOpenInfoRequest(foiOpenInfoRequest));
          dispatch(setFOILoader(false));
        } else {
          console.log("Error while fetching FOIOpenInfoRequest data", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error while fetching FOIOpenInfoRequest data", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
      });
  };
};

export const saveFOIOpenInfoRequest = (
  foiministryrequestid,
  foirequestId,
  data,
  isOIUser,
  requetsinfo,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_OPENINFO_REQUEST, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const done = fnDone(rest);
  const isValidExemptionRequest = !isOIUser && data.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish && data.oiexemption_id !== OIExemptions.OutsideScopeOfPublication;
  const isValidExemptionDenial = isOIUser && data.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish && data.oiexemption_id !== OIExemptions.OutsideScopeOfPublication && data.oiexemptionapproved === false;
  const isValidExemptionApproved = isOIUser && data.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish && data.oiexemption_id !== OIExemptions.OutsideScopeOfPublication && data.oiexemptionapproved === true;
  const manualPublicationStatusChange = requetsinfo.oistatusid === OIStates.ExemptionRequest && data.oipublicationstatus_id === OIPublicationStatuses.Publish;  
  if (isValidExemptionDenial) {
    data.oipublicationstatus_id = 2;
    data.oiexemption_id = null;
  }
  return (dispatch) => {
    updateFOIMinistryRequestOIStatus(foiministryrequestid, foirequestId, isValidExemptionRequest, isValidExemptionDenial, manualPublicationStatusChange, isValidExemptionApproved)
      .then((res) => {
        // If res.data.sucess (meaning BE call to update FOIMinistryRequest oistatusid for IAO OI Exemption purposes is successfull) =>
        // create and store an exemption date for the related foiopeninfo request
        if (res.data?.success && isValidExemptionRequest) {
          data.receiveddate = new Date();
        }
        if (res.data?.success && (isValidExemptionDenial || manualPublicationStatusChange)) {
          data.receiveddate = null;
        }
        httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data) {
          done(null, res.data);
          // dispatch(setFOILoader(false));
        } else {
          console.log("Error while updating FOIOpenInfoRequest data", res);
          dispatch(serviceActionError(res));
          // dispatch(setFOILoader(false));
        }
      });
      })
      .catch((error) => {
        done(error);
        console.log("Error while updating FOIOpenInfoRequest data", error);
        dispatch(serviceActionError(error));
        // dispatch(setFOILoader(false));
      });
  };
};

export const publishFOIOpenInfoRequest = (foiministryrequestid, foirequestid, data, ...rest) => {
  const openInfoApiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_OPENINFO_REQUEST, "<foirequestid>", foirequestid),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const openInfoPublishNowApi = replaceUrl(API.FOI_PUBLISHNOW_OPEN_INFORMATION, "<foiministryrequestid>", foiministryrequestid);
  const done = fnDone(rest);
  return (dispatch) => {
    // Update FOIOpenInfo data (publishdate, oipublcaitonstatus)
    httpPOSTRequest(openInfoApiUrl, data, UserService.getToken())
    .then((res) => {
      // Create a publish now message and add to redis queue
      httpPOSTRequest(openInfoPublishNowApi, {}, UserService.getToken())
      .then((res) => {
        if (res.status === 202 || res.status === 200) {
            done(null, res);
        } else {
          done(true, null);
          console.log("API call to publish request did not return status 201:", res);
          dispatch(serviceActionError(res));
        }
      })
    })
    .catch((error) => {
      done(error, null);
      console.log("API call to publish request failed", error);
      dispatch(serviceActionError(error));
    });
  };
}

export const unpublishFOIOpenInfoRequest = (foiministryrequestid, foirequestid, data, ...rest) => {
  const openInfoApiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_OPENINFO_REQUEST, "<foirequestid>", foirequestid),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const openInfoUnpublishApi = replaceUrl(API.FOI_UNPUBLISH_OPEN_INFORMATION, "<foiministryrequestid>", foiministryrequestid);
  const done = fnDone(rest);
  return (dispatch) => {
    // Update FOIOpenInfo data (publishdate, oipublcaitonstatus)
    httpPOSTRequest(openInfoApiUrl, data, UserService.getToken())
    .then((res) => {
      // Create a unpublish message and add to redis queue
      httpPOSTRequest(openInfoUnpublishApi, {}, UserService.getToken())
      .then((res) => {
        if (res.status === 202 || res.status === 200) {
            done(null, res);
        } else {
          done(true, null);
          console.log("API call to unpublish request did not return status 201:", res);
          dispatch(serviceActionError(res));
        }
      })
    })
    .catch((error) => {
      done(error, null);
      console.log("API call to unpublish request failed", error);
      dispatch(serviceActionError(error));
    });
  };
}

const updateFOIMinistryRequestOIStatus = (
  foiministryrequestid, 
  foirequestId, 
  isValidExemptionRequest,
  isValidExemptionDenial,
  manualPublicationStatusChange,
  isValidExemptionApproved
) => {
  let apiUrl= replaceUrl(replaceUrl(
    API.FOI_REQUEST_SECTION_API,
    "<ministryid>",
    foiministryrequestid),"<requestid>", foirequestId
  );
  // Update FOIMinistryRequest oistatusid to "Do Not Publish" if EXEMPTION is required from IAO
  if (isValidExemptionRequest) {
    return httpPOSTRequest(`${apiUrl}/oistatusid`, { oistatusid: OIStates.ExemptionRequest });
  // Update FOIMinistryRequest oistatusid to "Null" if Exemption Request denied OR if OpenInfo Publication status is manually changed from "Do not Publish" to Publish  
  } else if (isValidExemptionDenial || manualPublicationStatusChange) {
    return httpPOSTRequest(`${apiUrl}/oistatusid`, { oistatusid: null });
  } else if (isValidExemptionApproved) {
    return httpPOSTRequest(`${apiUrl}/oistatusid`, { oistatusid: OIStates.DoNotPublish });
  } else {
    return Promise.resolve("API call to adjust foiministryrequest not needed");
  }
};

export const fetchFOIOpenInfoAdditionalFiles = (foirequestId, foiministryrequestid) => {
  if (!foiministryrequestid) {
    return () => {};
  }
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_OPENINFO_ADDITIONAL_FILES, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const files = res.data;
          dispatch(setFOIOpenInfoAdditionalFiles(files));
          dispatch(setFOILoader(false));
        } else {
          console.log("Error while fetching FOIOpenInfoRequest data", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error while fetching FOIOpenInfoRequest data", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
      });
  }
};

export const deleteFOIOpenInfoAdditionalFiles = (
  foiministryrequestid,
  foirequestId,
  data,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_DELETE_OPENINFO_ADDITIONAL_FILES, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const done = fnDone(rest);
  return (dispatch) => {
    httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data) {
          done(null, res.data);
          dispatch(setFOILoader(false));
        } else {
          console.log("Error while deleting FOIAdditionalFiles data", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        done(error);
        console.log("Error while deleting FOIAdditionalFiles data", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
      });
  };
};

export const saveFOIOpenInfoAdditionalFiles = (
  foirequestId,
  foiministryrequestid,
  data,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_OPENINFO_ADDITIONAL_FILES, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const done = fnDone(rest);
  return (dispatch) => {
    httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data) {
          done(null, res.data);
          // dispatch(setFOILoader(false));
        } else {
          console.log("Error while saving FOIAdditionalFiles data", res);
          dispatch(serviceActionError(res));
          // dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        done(error);
        console.log("Error while saving FOIAdditionalFiles data", error);
        dispatch(serviceActionError(error));
        // dispatch(setFOILoader(false));
      });
  };
};
