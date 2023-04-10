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
import { replaceUrl } from "../../../helper/FOI/helper";
import { catchError, fnDone } from "./foiServicesUtil";
import UserService from "../../../services/UserService";


export const fetchProgramAreaDivisions = () => {
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_PROGRAMAREADIVISIONS, {}, UserService.getToken())
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
        catchError(error, dispatch);
      });
  };
};

export const createProgramAreaDivision = (data, ...rest) => {
  const done = fnDone(rest);
  return (dispatch) => {
    httpPOSTRequest(API.FOI_POST_PROGRAMAREADIVISION, data, UserService.getToken())
      .then((res) => {
        dispatch(fetchProgramAreaDivisions());
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error creating program area division`);
        }
      })
      .catch((error) => {
        //dispatch(serviceActionError(error));
        done(error);
        catchError(error, dispatch);
        console.log("Error creating program area division");
      });
  };
};

export const editProgramAreaDivision = (data, divisionid, ...rest) => {
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_PUT_PROGRAMAREADIVISIONS),
    "<divisionid>",
    divisionid
  );
  return (dispatch) => {
    httpPUTRequest(apiUrl, data, UserService.getToken())
      .then((res) => {
        dispatch(fetchProgramAreaDivisions());
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error editing program area division`);
        }
      })
      .catch((error) => {
        done(error);
        catchError(error, dispatch);
      });
  };
};

export const disableProgramAreaDivision = (divisionid, ...rest) => {
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_DELETE_PROGRAMAREADIVISIONS),
    "<divisionid>",
    divisionid
  );
  return (dispatch) => {
    httpPUTRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        dispatch(fetchProgramAreaDivisions());
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error disabling program area division");
        }
      })
      .catch((error) => {
        done(error);
        catchError(error, dispatch);
        console.log("Error disabling program area division");
      });
  };
};
