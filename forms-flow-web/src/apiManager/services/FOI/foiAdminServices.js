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
import { catchError } from "./foiServicesUtil";

export const fetchProgramAreaDivisions = () => {
  return (dispatch) => {
    httpGETRequest(API.FOI_GET_PROGRAMAREADIVISIONS)
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

export const createProgramAreaDivision = (data) => {
  return (dispatch) => {
    httpPOSTRequest(API.FOI_POST_PROGRAMAREADIVISION, data)
      .then((res) => {
        dispatch(fetchProgramAreaDivisions());
        if (res.data) {
          console.log("Create program area division successfully!");
        } else {
          dispatch(serviceActionError(res));
          console.log("Error creating program area division");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        console.log("Error creating program area division");
      });
  };
};

export const editProgramAreaDivision = (data, divisionid) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_PUT_PROGRAMAREADIVISIONS),
    "<divisionid>",
    divisionid
  );
  return (dispatch) => {
    httpPUTRequest(apiUrl, data)
      .then((res) => {
        dispatch(fetchProgramAreaDivisions());
        if (res.data) {
          console.log("Edit program area division successfully!");
        } else {
          dispatch(serviceActionError(res));
          console.log("Error editing program area division");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        console.log("Error editing program area division");
      });
  };
};

export const disableProgramAreaDivision = (divisionid) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_DELETE_PROGRAMAREADIVISIONS),
    "<divisionid>",
    divisionid
  );
  return (dispatch) => {
    httpPUTRequest(apiUrl)
      .then((res) => {
        dispatch(fetchProgramAreaDivisions());
        if (res.data) {
          console.log("Disable program area division successfully!");
        } else {
          dispatch(serviceActionError(res));
          console.log("Error disabling program area division");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        console.log("Error disabling program area division");
      });
  };
};
