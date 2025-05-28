import { httpPOSTRequest, httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  serviceActionError,
  setFOILoader,
  setFOIRequestConsults
} from "../../../actions/FOI/foiRequestActions";
import { fnDone, catchError } from "./foiServicesUtil";
// import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper";
// import { OIStates, OIPublicationStatuses, OIExemptions } from "../../../helper/openinfo-helper";

export const fetchFOIRequestConsults = (foiministryrequestid) => {
  if (!foiministryrequestid) {
    return () => {};
  }
  const foiConsultsRequestAPIUrl = replaceUrl(
    replaceUrl(API.FOI_GET_REQUEST_CONSULTS),
    "<ministryrequestid>",
    foiministryrequestid
  );
  return (dispatch) => {
    httpGETRequest(foiConsultsRequestAPIUrl, {})
      .then((res) => {
        if (res.data) {
          const foiConsultRequests = Array.isArray(res.data) ? res.data : [res.data];
          dispatch(setFOIRequestConsults(foiConsultRequests));
          dispatch(setFOILoader(false));
        } else {
          console.log("Error while fetching FOIConsultationRequest data", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error while fetching FOIConsultationRequest data", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
      });
  };
};


export const saveFOIRequestConsults = (requestId, ministryId, data, ...rest) => {
  const done = fnDone(rest);
  let apiUrl = replaceUrl(replaceUrl(
      API.FOI_POST_REQUEST_CONSULTS,
      "<foirequestid>",
      requestId
    ), "<foiministryrequestid>", ministryId);

    return (dispatch) => {
      httpPOSTRequest(apiUrl, data)
        .then((res) => {
          if (res.data) {
            done(null, res.data);
            dispatch(setFOIRequestConsults(res.data));
          } else {
            dispatch(serviceActionError(res));
            throw new Error(`Error while saving the ministry request (request# ${requestId}, ministry# ${ministryId})`);            
          }
        })
        .catch((error) => {
          done(error);
          catchError(error, dispatch);
        });
    };
};
