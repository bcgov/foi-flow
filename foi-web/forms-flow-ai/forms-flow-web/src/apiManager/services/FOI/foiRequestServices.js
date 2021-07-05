import { httpGETRequest, httpPOSTRequest, httpOpenGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  setFOIRequestList,
  serviceActionError,
  setFOILoader,
  //setFOIRequestDetail,
} from "../../../actions/FOI/foiRequestActions";
import { foiRequestDataFormatter } from "./foiFormatterService";
import UserService from "../../../services/UserService";

export const fetchFOIRequestList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  return (dispatch) => {
    httpOpenGETRequest(API.FOI_GET_REQUESTS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequests = res.data;
          //console.log(`RequestList = ${JSON.stringify(foiRequests)}`)
          let data = foiRequests.map((foiRequest) => {
            //const foiRequestData = foiRequestDataFormatter(foiRequest.variables);
            //delete foiRequest.variables;
            //return { ...foiRequest, ...foiRequestData };
            return { ...foiRequest};
          });
          dispatch(setFOIRequestList(data));
          dispatch(setFOILoader(false));
          done(null, res.data);
        } else {
          console.log("Error", res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log("Error", error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
        done(error);
      });
  };
};
