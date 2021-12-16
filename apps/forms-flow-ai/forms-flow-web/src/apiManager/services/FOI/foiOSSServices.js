import {
    httpPOSTRequest,
    httpOSSPUTRequest,
    httpOSSGETRequest,
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
  } from "../../../actions/FOI/foiRequestActions";
  import { saveAs } from "file-saver";
  
    
  export const getOSSHeaderDetails = (data, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    return (dispatch) => {
      httpPOSTRequest(API.FOI_POST_OSS_HEADER, data)
        .then((res) => {
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
    };
  };
  
  export const saveFilesinS3 = (headerDetails, file, ...rest) => {
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    var requestOptions = {
      headers: {
        'X-Amz-Date': headerDetails.amzdate,
        'Authorization': headerDetails.authheader,
      }
    };
    return (dispatch) => {
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
  };
  
  export const getFileFromS3 = (headerDetails, file, ...rest) => {  
    const done = rest.length ? rest[0] : () => {
        //This is intentional
     };
    var requestOptions = {
      headers: {
        "X-Amz-Date": headerDetails.amzdate,
        Authorization: headerDetails.authheader,     
      },
      responseType: 'blob'
    };  
    return (dispatch) => {    
      httpOSSGETRequest(headerDetails.filepath, requestOptions)
      .then((res) => {
          var blob = new Blob([res.data], {type: "application/octet-stream"});
          saveAs(blob, file.filename)
          if (res) {
            done(null, res.status);
          } else {
            dispatch(serviceActionError(res));
            done("Error in getting files from S3");
          }
        })
        .catch((error) => {
          console.log(error);
          dispatch(serviceActionError(error));
          done("Error in getting files from S3");
        });
    };
  };
  
  