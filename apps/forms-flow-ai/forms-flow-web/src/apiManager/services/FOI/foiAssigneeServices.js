import {
    httpPOSTRequest
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError
  } from "../../../actions/FOI/foiRequestActions";
  import { replaceUrl } from "../../../helper/FOI/helper";
  import { catchError, fnDone } from "./foiServicesUtil";


  export const saveAssignee = (data, requestId, ministryId, isMinistryCoordinator, ...rest) => {
    const done = fnDone(rest);
    if (ministryId)
      return saveFOIMinistryRequestAssignee(data, requestId, ministryId, isMinistryCoordinator, done)
    else
      return saveFOIRawRequestAssignee(data, requestId, done)
  
};

const saveFOIMinistryRequestAssignee = (data, requestId, ministryId, isMinistryCoordinator, done) => {
  let userType = "iao";
    if (isMinistryCoordinator)
      userType = "ministry"
    let apiUrl = "";
    if (ministryId) {
      apiUrl = replaceUrl(replaceUrl(replaceUrl(
        API.FOI_REQUEST_ASSIGNEE_API,
        "<requestid>",
        requestId
      ), "<ministryid>", ministryId), "<usertype>",userType);
      return (dispatch) => {
        httpPOSTRequest(apiUrl, data)
          .then((res) => {
            if (res.data) {
              done(null, res.data);
            } else {
              dispatch(serviceActionError(res));
              throw new Error(`Error while saving the Assgnee for the (request# ${requestId}, ministry# ${ministryId})`);            
            }
          })
          .catch((error) => {
            done(error);
            catchError(error, dispatch);
          });
      };
    }
  }

  const saveFOIRawRequestAssignee = (data, requestId, done) => {
    const apiUrl = replaceUrl(
      API.FOI_RAWREQUEST_ASSIGNEE_API,
      "<requestid>",
      requestId
    );

    return (dispatch) => {
      httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error while saving the Assgnee for the (request# ${requestId})`);            
        }
      })
      .catch((error) => {
        done(error);
        catchError(error, dispatch);
      });
    };
  }
