import { httpPOSTRequest, httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  serviceActionError,
  setFOILoader,
  setFOIOpenInfoRequest,
} from "../../../actions/FOI/foiRequestActions";
import { fnDone } from "./foiServicesUtil";
import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper";
import { OIStates } from "../../../helper/openinfo-helper";

export const fetchFOIProactiveDisclosureRequest = (foiministryrequestid) => {
  if (!foiministryrequestid) {
    return () => {};
  }
  const apiUrl = replaceUrl(
    API.FOI_GET_PROACTIVE_DISCLOSURE_REQUEST,
    "<ministryrequestid>",
    foiministryrequestid
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const proactiveRequest = res.data;
          // We can reuse setFOIOpenInfoRequest since the data structure is similar for the UI tab
          dispatch(setFOIOpenInfoRequest(proactiveRequest));
          dispatch(setFOILoader(false));
        } else {
          console.log("Error while fetching FOI Proactive Disclosure Request data", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error while fetching FOI Proactive Disclosure Request data", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
      });
  };
};

export const saveFOIProactiveDisclosureRequest = (
  foiministryrequestid,
  foirequestId,
  data,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_PROACTIVE_DISCLOSURE_REQUEST, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const done = fnDone(rest);
  return (dispatch) => {
    httpPOSTRequest(apiUrl, data, UserService.getToken())
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          console.log("Error while updating FOI Proactive Disclosure Request data", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        done(error);
        console.log("Error while updating FOI Proactive Disclosure Request data", error);
        dispatch(serviceActionError(error));
      });
  };
};

const updateFOIMinistryRequestOIStatus = (
  foiministryrequestid, 
  foirequestId
) => {
  let apiUrl= replaceUrl(replaceUrl(
    API.FOI_REQUEST_SECTION_API,
    "<ministryid>",
    foiministryrequestid),"<requestid>", foirequestId
  );
  return httpPOSTRequest(`${apiUrl}/oistatusid`, { oistatusid: OIStates.Published });
};

export const publishFOIProactiveDisclosureRequest = (foiministryrequestid, foirequestId, data, ...rest) => {
  const proactiveDisclosureApiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_PROACTIVE_DISCLOSURE_REQUEST, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const pdPublishNowApi = replaceUrl(API.FOI_PUBLISHNOW_PROACTIVE_DISCLOSURE, "<foiministryrequestid>", foiministryrequestid);
  const done = fnDone(rest);
  return (dispatch) => {
    // Update FOIPDrequest data (publishdate, oipublcaitonstatus)
    httpPOSTRequest(proactiveDisclosureApiUrl, data, UserService.getToken())
    .then((res) => {
      // Create a publish now message and add to redis queue
      httpPOSTRequest(pdPublishNowApi, {}, UserService.getToken())
      .then((res) => {
        if (res.status === 202) {
            done(null, res.data);
        } else {
          console.log("API call to publish request did not return status 201:", res);
          dispatch(serviceActionError(res));
        }
      })
    })
    .catch((error) => {
      done(error);
      console.log("API call to publish request failed", error);
      dispatch(serviceActionError(error));
    });
  };
}

export const unpublishFOIProactiveDisclosureRequest = (foiministryrequestid, foirequestId, data, ...rest) => {
  const pdUnpublishApi= replaceUrl(API.FOI_UNPUBLISH_PROACTIVE_DISCLOSURE, "<foiministryrequestid>", foiministryrequestid);
  const proactiveDisclosureApiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_PROACTIVE_DISCLOSURE_REQUEST, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const done = fnDone(rest);
  return (dispatch) => {
    // Update FOIPDrequest data (oipublcaitonstatus)
    httpPOSTRequest(proactiveDisclosureApiUrl, data, UserService.getToken())
    .then((res) => {
      // Create a unpublish message and add to redis queue
      httpPOSTRequest(pdUnpublishApi, {}, UserService.getToken())
      .then((res) => {
        if (res.status === 202) {
            done(null, res.data);
        } else {
          console.log("API call to unpublish request did not return status 201:", res);
          dispatch(serviceActionError(res));
        }
      })
    })
    .catch((error) => {
      done(error);
      console.log("API call to unpublish request failed", error);
      dispatch(serviceActionError(error));
    });
  };
}
