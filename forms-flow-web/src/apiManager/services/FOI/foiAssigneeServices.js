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

export const saveConsultAssignee = (data, ministryId, consultId, isMinistryCoordinator, ...rest) => {
  const done = fnDone(rest);
  if (consultId)
    return saveFOIMinistryConsultRequestAssignee(data, ministryId, consultId, isMinistryCoordinator, done)
  else 
    return saveFOIRawConsultRequestAssignee(data, ministryId, done)
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

  const saveFOIMinistryConsultRequestAssignee = (data, ministryId, consultId, isMinistryCoordinator, done) => {
    let userType = "iao";
      if (isMinistryCoordinator)
        userType = "ministry"
      let apiUrl = "";
      if (ministryId && consultId) {
        apiUrl = replaceUrl(replaceUrl(replaceUrl(
          API.FOI_POST_MINISTRY_CONSULT_REQUEST_ASSIGNEE_API,
          "<ministryid>",
          ministryId
        ), "<consultid>", consultId), "<usertype>", userType);
        return (dispatch) => {
          httpPOSTRequest(apiUrl, data)
            .then((res) => {
              if (res.data) {
                done(null, res.data);
              } else {
                dispatch(serviceActionError(res));
                throw new Error(`Error while saving the Assgnee for the (ministry# ${ministryId})`);            
              }
            })
            .catch((error) => {
              done(error);
              catchError(error, dispatch);
            });
        };
      }
    }

    const saveFOIRawConsultRequestAssignee = (data, requestId, ministryId, done) => {
      let apiUrl = replaceUrl(replaceUrl(
        API.FOI_POST_RAW_CONSULT_REQUEST_ASSIGNEE_API,
        "<foirequestid>",
        requestId
      ), "<foiministryrequestid>", ministryId);
  
      return (dispatch) => {
        httpPOSTRequest(apiUrl, data)
        .then((res) => {
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            throw new Error(`Error while saving the Assgnee for the (request# ${ministryId})`);            
          }
        })
        .catch((error) => {
          done(error);
          catchError(error, dispatch);
        });
      };
    }