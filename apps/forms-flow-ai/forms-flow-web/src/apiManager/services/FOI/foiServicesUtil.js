import {
    httpPOSTRequest,
} from "../../httpRequestHandler";
import {
    serviceActionError,
    setFOIAttachmentListLoader,
  } from "../../../actions/FOI/foiRequestActions";

import { fetchFOIRequestAttachmentsList } from "./foiAttachmentServices";

export const postAttachment = (dispatch, apiUrl, data, requestId, ministryId, errorMessage, done) => {    
    httpPOSTRequest(apiUrl, data)
        .then((res) => {          
          if (res.data) {
            dispatch(fetchFOIRequestAttachmentsList(requestId,ministryId));
            dispatch(setFOIAttachmentListLoader(false));           
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            dispatch(setFOIAttachmentListLoader(false));
            done(errorMessage);
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          dispatch(setFOIAttachmentListLoader(false));
          done(errorMessage);
        });
}