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
