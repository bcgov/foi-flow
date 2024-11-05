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
  data
) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_POST_OPENINFO_REQUEST, "<foirequestid>", foirequestId),
    "<foiministryrequestid>",
    foiministryrequestid
  );
  return (dispatch) => {
    httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data) {
          dispatch(setFOILoader(false));
        } else {
          console.log("Error while updating FOIOpenInfoRequest data", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error while updating FOIOpenInfoRequest data", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
      });
  };
};
