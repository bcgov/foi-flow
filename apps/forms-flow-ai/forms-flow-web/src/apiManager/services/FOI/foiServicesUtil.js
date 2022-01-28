import {
    httpPOSTRequest,
} from "../../httpRequestHandler";
import {
    serviceActionError,
    setFOIAttachmentListLoader,
    setFOILoader,
  } from "../../../actions/FOI/foiRequestActions";

import { fetchFOIRequestAttachmentsList } from "./foiAttachmentServices";


export const catchError = (error, dispatch) => {
  console.log(error);
  dispatch(serviceActionError(error));
  dispatch(setFOILoader(false));    
}

export const fnDone = (rest) => {
  return rest.length ? rest[0] : () => {
    //This is intentional
 };
}

export const postAttachment = (dispatch, apiUrl, data, requestId, ministryId, errorMessage, rest) => {
    const done = fnDone(rest);
    httpPOSTRequest(apiUrl, data)
        .then((res) => {          
          if (res.data) {
            dispatch(fetchFOIRequestAttachmentsList(requestId,ministryId));
            dispatch(setFOIAttachmentListLoader(false));
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            throw new Error(errorMessage);
          }
        })
        .catch((error) => {
          catchError(error, dispatch);
        });
}

