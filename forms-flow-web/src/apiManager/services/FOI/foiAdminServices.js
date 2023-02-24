import {
  httpPOSTRequest,
  httpGETRequest,
  httpPUTRequest,
} from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  serviceActionError,
  setFOILoader,
  setFOIProgramAreaDivisionsList,
} from "../../../actions/FOI/foiRequestActions";
import { replaceUrl, errorToast } from "../../../helper/FOI/helper";
import { catchError } from './foiServicesUtil';

export const fetchProgramAreaDivisions = () => {
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_PROGRAMAREADIVISIONS_API)
      .then((res) => {
        if (res.data) {
          dispatch(setFOIProgramAreaDivisionsList(res.data));
          dispatch(setFOILoader(false));
        } else {
          console.log("Error in fetching program area divisions", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        catchError(error, dispatch)
      })
  }
}
