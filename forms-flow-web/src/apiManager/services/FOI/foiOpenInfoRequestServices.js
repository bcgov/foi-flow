import { httpPOSTRequest, httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  serviceActionError,
  setFOILoader,
  setFOIOpenInfoRequest,
} from "../../../actions/FOI/foiRequestActions";
import { fnDone, catchError } from "./foiServicesUtil";
import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper";

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
  requetsinfo,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_OPENINFO_REQUEST, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  const done = fnDone(rest);
  return (dispatch) => {
    updateFOIMinistryRequestOIStatus(foiministryrequestid, foirequestId, data, requetsinfo)
      .then((res) => {
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
  requetsinfo
) => {
  let apiUrl= replaceUrl(replaceUrl(
    API.FOI_REQUEST_SECTION_API,
    "<ministryid>",
    foiministryrequestid),"<requestid>", foirequestId
  );
  if (!requetsinfo.oistatusid && foiopeninfodata.oiexemption_id !== 5) {
    return httpPOSTRequest(`${apiUrl}/oistatusid`, { oistatusid: 2 });
  } else {
    return Promise.resolve("API call to adjust foiministryrequest not needed");
  }
};
