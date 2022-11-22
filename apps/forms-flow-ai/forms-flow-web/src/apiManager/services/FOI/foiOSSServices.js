import {
    httpPOSTRequest,
    httpOSSPUTRequest,
    httpOSSGETRequest,httpGETRequest
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
  } from "../../../actions/FOI/foiRequestActions";
  import { fnDone } from "./foiServicesUtil";
  import UserService from "../../../services/UserService";
  
  export const getOSSHeaderDetails = (data, dispatch, ...rest) => {
    const done = fnDone(rest);
    const response = httpPOSTRequest(API.FOI_POST_OSS_HEADER, data);
    response.then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          done("Error in getting OSS Header information");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done("Error in getting OSS Header information");
      });
    return response;
  };
  
  export const saveFilesinS3Async = async (headerDetails, file, dispatch, ...rest) => {
    const done = fnDone(rest);
    let requestOptions = {
      headers: {
        "X-Amz-Date": headerDetails.amzdate,
        Authorization: headerDetails.authheader,
      },
    };
    httpOSSPUTRequest(headerDetails.filepath, file, requestOptions)
      .then((res) => {
        if (res) {
          done(null, res.status);
        } else {
          dispatch(serviceActionError(res));
          done("Error in saving files to S3");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done("Error in saving files to S3");
      });
  };
  
  export const saveFilesinS3 = (headerDetails, file, dispatch, ...rest) => {
    const done = fnDone(rest);
    let requestOptions = {
      headers: {
        'X-Amz-Date': headerDetails.amzdate,
        'Authorization': headerDetails.authheader,
      }
    };
    return httpOSSPUTRequest(headerDetails.filepath, file, requestOptions)
      .then((res) => {
        if (res) {
          done(null, res.status);
        } else {
          done("Error in saving files to S3");
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(error);
      });
  };
  
  export const getFileFromS3 = (headerDetails, ...rest) => {  
    const done = fnDone(rest);
    let requestOptions = {
      headers: {
        "X-Amz-Date": headerDetails.amzdate,
        Authorization: headerDetails.authheader,     
      },
      responseType: 'blob'
    };  
    return httpOSSGETRequest(headerDetails.filepath, requestOptions)
      .then((res, dispatch) => {
        if (res) {
          done(null, res);
        } else {
          dispatch(serviceActionError(res));
          done("Error in getting files from S3");
        }
      })
      .catch((error, dispatch) => {
        console.log(error);
        dispatch(serviceActionError(error));
        done("Error in getting files from S3");
      });
  };

  export const getFOIS3DocumentPreSignedUrl = (filepath,ministryrequestid,dispatch,...rest) => {
    const done = fnDone(rest);
    const type = rest[1] || 'attachments';
    const bcgovcode = rest[2];
    console.log(ministryrequestid)
    const apiurl = API.FOI_GET_S3DOCUMENT_PRESIGNEDURL+ "/" + (ministryrequestid == undefined ? "-1" : ministryrequestid) +"/" + type + "/" + bcgovcode + "?filepath="+filepath
    const response = httpGETRequest(apiurl, {}, UserService.getToken());
    response.then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          done("Error in getFOIS3DocumentPreSignedUrl");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done("Error in getFOIS3DocumentPreSignedUrl");
      });
    return response;
  };
  
  export const postFOIS3DocumentPreSignedUrl = (ministryrequestid, data, category, bcgovcode, dispatch, ...rest) => {
    const done = fnDone(rest);
    const apiurl = API.FOI_POST_S3DOCUMENT_PRESIGNEDURL+ "/" + (ministryrequestid == undefined ? "-1" : ministryrequestid) + "/" + category + "/" + bcgovcode;
    const response = httpPOSTRequest(apiurl, data, UserService.getToken());
    response.then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          done("Error in postFOIS3DocumentPreSignedUrl");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done("Error in postFOIS3DocumentPreSignedUrl");
      });
    return response;
  };
  