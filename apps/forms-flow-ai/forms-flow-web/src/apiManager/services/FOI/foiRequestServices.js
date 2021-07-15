import { httpGETRequest, httpPOSTRequest, httpOpenGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  setFOIRequestList,
  serviceActionError,
  setFOILoader,
  setFOIRequestDetail,
  setFOICategoryList,
  setFOIProgramAreaList,
  clearRequestDetails,
} from "../../../actions/FOI/foiRequestActions";
import UserService from "../../../services/UserService";
import {replaceUrl} from "../../../helper/helper";

export const fetchFOIRequestList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  return (dispatch) => {
    httpOpenGETRequest(API.FOI_GET_REQUESTS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequests = res.data;         
          let data = foiRequests.map((foiRequest) => {
            //const foiRequestData = foiRequestDataFormatter(foiRequest.variables);
            //delete foiRequest.variables;
            //return { ...foiRequest, ...foiRequestData };
            return { ...foiRequest};
          });
          dispatch(clearRequestDetails({}));
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

export const fetchFOIRequestDetails = (requestId,...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const apiUrlgetRequestDetails = replaceUrl(
    API.FOI_GET_REQUEST_API,
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpOpenGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequest = res.data;

          // let data = foiRequests.map((foiRequest) => {
          //   //const foiRequestData = foiRequestDataFormatter(foiRequest.variables);
          //   //delete foiRequest.variables;
          //   //return { ...foiRequest, ...foiRequestData };
          //   return { ...foiRequest};
          // });

          dispatch(setFOIRequestDetail(foiRequest));
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

export const fetchFOICategoryList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};
  const firstCategory = {"applicantcategoryid": 0, "name": "Select Category"};
  return (dispatch) => {
    httpOpenGETRequest(API.FOI_GET_CATEGORIES_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiRequestCategoryList = res.data;         
          let data = foiRequestCategoryList.map((category) => {
            return { ...category};
          });
          data.unshift(firstCategory);
          dispatch(setFOICategoryList(data));
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

export const fetchFOIProgramAreaList = (...rest) => {
  const done = rest.length ? rest[0] : () => {};  
  return (dispatch) => {
    httpOpenGETRequest(API.FOI_GET_PROGRAMAREAS_API, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiProgramAreaList = res.data;         
          let data = foiProgramAreaList.map((programArea) => {
            return { ...programArea, isChecked: false};
          });
          dispatch(setFOIProgramAreaList(data));
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