import {
    httpPOSTRequest,
    httpOSSPUTRequest,
    httpOSSGETRequest,
    httpGETRequest
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
        'Content-Type': 'application/octet-stream'
      },
    };
    try {
    let response = httpOSSPUTRequest(headerDetails.filepath, file, requestOptions)
    response.then((res) => {
        if (res) {
          done(null, res.status);
        } else {
          done("Error in saving files to S3");
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done("Error in saving files to S3");
      });
    return response;
    } catch (error) {
      console.error("Error:", error);
    }
  };
  
  export const getFileFromS3 = (headerDetails, ...rest) => {  
    const done = fnDone(rest);
    let requestOptions = {
      headers: {
        "X-Amz-Date": headerDetails.amzdate,
        Authorization: headerDetails.authheader,     
      },
      responseType: 'blob',
      onDownloadProgress: rest[1]
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
  
  export const postFOIS3DocumentPreSignedUrl = (ministryrequestid = -1, data, category="attachments", bcgovcode="Misc", dispatch, ...rest) => {	
    const done = fnDone(rest);
    const apiurl = API.FOI_POST_S3DOCUMENT_PRESIGNEDURL+ "/" + ministryrequestid + "/" + category + "/" + bcgovcode;
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

  export const completeMultiPartUpload = (data, ministryrequestid = -1, category, bcgovcode, dispatch, ...rest) => {
    const done = fnDone(rest);
    const response = httpPOSTRequest(API.FOI_POST_COMPLETE_UPLOAD + '/' + ministryrequestid + '/' + category + '/' + bcgovcode, data);
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

  export const downloadFileFromS3 = (headerDetails, ...rest) => {
    const done = fnDone(rest);

    const requestOptions = {
      headers: {
        "X-Amz-Date": headerDetails.amzdate,
        Authorization: headerDetails.authheader,
      },
      responseType: "blob",
      onDownloadProgress: rest[1],
      validateStatus: () => true, // allows 404, 403 etc. without throwing
    };

    return httpOSSGETRequest(headerDetails.filepath, requestOptions)
      .then((res) => {
        if (res && res.status === 200) {
          done(null, res);
        } else {
          // surface the error response, not just a string
          done({ message: "File not found", status: res.status }, res);
        }
      })
      .catch((error) => {
        // Still catch actual network issues
        console.error("S3 fetch failed:", error);
        done(error, null);
      });
  };

  
