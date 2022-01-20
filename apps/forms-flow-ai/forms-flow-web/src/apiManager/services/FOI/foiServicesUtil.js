import {
    httpPOSTRequest,
} from "../../httpRequestHandler";
import {
    serviceActionError,
    setFOIAttachmentListLoader,
    setFOILoader,
  } from "../../../actions/FOI/foiRequestActions";

import { fetchFOIRequestAttachmentsList } from "./foiAttachmentServices";
import { StateEnum } from '../../../constants/FOI/statusEnum';
import MinistriesCanvassed from "../../../components/FOI/customComponents/MinistriesCanvassed/MinistriesCanvassed";

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

export const setRedirectUrl = (foiRequest,notification,isMinistry) =>{
  Object.entries(StateEnum).forEach(([key, value]) =>{
    if(key && value.id === foiRequest.requeststatusid){
      let url = "";
      if(notification.requesttype === 'rawrequest'){
        url=`/foi/reviewrequest/${notification.requestid}/${value.name}`;
      }
      else if(notification.requesttype === 'ministryrequest'){
        if(isMinistry)
          url = `/foi/ministryreview/${notification.foirequestid}/ministryrequest/${notification.requestid}/${value.name}`;
        else
          url = `/foi/foirequests/${notification.foirequestid}/ministryrequest/${notification.requestid}/${value.name}`;
      }
      window.location.href=url;
    }
  })
}

export const test1 = () =>{
    return(
      <MinistriesCanvassed  openModal={true} ></MinistriesCanvassed>
    );
}