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
  return (dispatch) => {
    updateFOIMinistryRequestOIStatus(foiministryrequestid, foirequestId, data, isOIUser, requetsinfo)
      .then((res) => {
        // If res.data.sucess (meaning BE call to update FOIMinistryRequest oistatusid for IAO OI Exemption purposes is successfull) =>
        // create and store an exemption date for the related foiopeninfo request
        if (res.data?.success && isValidExemptionRequest) {
          data.oiexemptiondate = new Date();
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

const updateFOIMinistryRequestOIStatus = (
  foiministryrequestid, 
  foirequestId, 
  foiopeninfodata,
  isOIUser, 
  requetsinfo
) => {
  let apiUrl= replaceUrl(replaceUrl(
    API.FOI_REQUEST_SECTION_API,
    "<ministryid>",
    foiministryrequestid),"<requestid>", foirequestId
  );
  const isValidExemptionRequest = !isOIUser && foiopeninfodata.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish && foiopeninfodata.oiexemption_id !== OIExemptions.OutsideScopeOfPublication;
  const isValidExemptionDenial = isOIUser && foiopeninfodata.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish && foiopeninfodata.oiexemption_id !== OIExemptions.OutsideScopeOfPublication && foiopeninfodata.oiexemptionapproved === false;
  const manualPublicationStatusChange = requetsinfo.oistatusid === OIStates.ExemptionRequest && foiopeninfodata.oipublicationstatus_id === OIPublicationStatuses.Publish;
  // Update FOIMinistryRequest oistatusid to "Do Not Publish" if EXEMPTION is required from IAO
  if (isValidExemptionRequest) {
    return httpPOSTRequest(`${apiUrl}/oistatusid`, { oistatusid: OIStates.ExemptionRequest });
  // Update FOIMinistryRequest oistatusid to "Null" if Exemption Request denied OR if OpenInfo Publication status is manually changed from "Do not Publish" to Publish  
  } else if (isValidExemptionDenial || manualPublicationStatusChange) {
    return httpPOSTRequest(`${apiUrl}/oistatusid`, { oistatusid: null });
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
  foiministryrequestid,
  foirequestId,
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
