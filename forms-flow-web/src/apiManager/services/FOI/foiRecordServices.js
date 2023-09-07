import {
  httpGETRequest,
  httpGETRequest1,
  httpPOSTRequest,
} from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  serviceActionError,
  setRequestRecords,
  setRecordFormats,
  setConversionFormats,
  setFOILoader,
  setFOIPDFStitchedRecordForHarms,
  setFOIPDFStitchStatusForHarms,
  setRecordsLoader,
  setFOIPDFStitchStatusForRedlines,
  setFOIPDFStitchedRecordForRedlines,
  setFOIPDFStitchStatusForResponsePackage,
  setFOIPDFStitchedRecordForResponsePackage,
} from "../../../actions/FOI/foiRequestActions";
import { fnDone } from "./foiServicesUtil";
import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper";
import { FOI_RECORD_FORMATS } from "../../../constants/constants";

export const fetchPDFStitchedRecordForHarms = (
  requestId,
  ministryId,
  ...rest
) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_DOWNLOAD_RECORDS_FOR_HARMS,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setFOIPDFStitchedRecordForHarms(res.data));
          done(null, res.data);
        } else {
          console.log("Error in fetching records for hamrs", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        console.log("Error in fetching records for harms", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const fetchPDFStitchStatusForHarms = (
  requestId,
  ministryId,
  ...rest
) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_PDF_STITCH_STATUS_FOR_HARMS,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setFOIPDFStitchStatusForHarms(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const checkForRecordsChange = (requestId, ministryId, ...rest) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_CHECK_RECORDS_CHANGED,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          if (res.data.recordchanged) {
            dispatch(setFOIPDFStitchStatusForHarms("not started"));
          }
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in checking for records change", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const fetchFOIRecords = (requestId, ministryId, ...rest) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_GET_RECORDS, "<ministryrequestid>", ministryId),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    dispatch(setRecordsLoader("inprogress"));
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setRequestRecords(res.data));
          dispatch(setRecordsLoader("completed"));
          done(null, res.data);
        } else {
          console.log("Error in fetching records", res);
          dispatch(serviceActionError(res));
          dispatch(setRecordsLoader("error"));
        }
      })
      .catch((error) => {
        console.log("Error in fetching records", error);
        dispatch(serviceActionError(error));
        dispatch(setRecordsLoader("error"));
        done(error);
      });
  };
};

export const fetchRedactedSections = (ministryId, ...rest) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    API.DOC_REVIEWER_REDACTED_SECTIONS,
    "<ministryrequestid>",
    ministryId
  );
  return (dispatch) => {
    dispatch(setRecordsLoader("inprogress"));
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setRecordsLoader("completed"));
          done(null, res.data);
        } else {
          console.log("Error in fetching redacted sections", res);
          dispatch(serviceActionError(res));
          dispatch(setRecordsLoader("error"));
        }
      })
      .catch((error) => {
        console.log("Error in fetching redacted section", error);
        dispatch(serviceActionError(error));
        dispatch(setRecordsLoader("error"));
        done(error);
      });
  };
};

export const saveFOIRecords = (requestId, ministryId, data, ...rest) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_GET_RECORDS, "<ministryrequestid>", ministryId),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    postRecord(dispatch, apiUrl, data, "Error in posting records", rest);
  };
};

export const retryFOIRecordProcessing = (
  requestId,
  ministryId,
  data,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_RETRY_RECORDS, "<ministryrequestid>", ministryId),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    postRecord(dispatch, apiUrl, data, "Error in triggering job retry", rest);
  };
};

export const replaceFOIRecordProcessing = (
  requestId,
  ministryId,
  recordid,
  data,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(
      replaceUrl(API.FOI_REPLACE_RECORDS, "<ministryrequestid>", ministryId),
      "<requestid>",
      requestId
    ),
    "<recordid>",
    recordid
  );
  return (dispatch) => {
    postRecord(dispatch, apiUrl, data, "Error in triggering job retry", rest);
  };
};

export const updateFOIRecords = (requestId, ministryId, data, ...rest) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_UPDATE_RECORDS, "<ministryrequestid>", ministryId),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    postRecord(dispatch, apiUrl, data, "Error in updating records", rest);
  };
};

export const deleteReviewerRecords = (filepaths, ...rest) => {
  const done = fnDone(rest);
  let apiUrl = API.DOC_REVIEWER_DELETE_RECORDS;
  return (dispatch) => {
    postRecord(dispatch, apiUrl, filepaths, "Error in deleting records", rest);
  };
};

export const triggerDownloadFOIRecordsForHarms = (
  requestId,
  ministryId,
  data,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_TRIGGER_DOWNLOAD_RECORDS_FOR_HARMS,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    postRecord(
      dispatch,
      apiUrl,
      data,
      "Error in posting records",
      rest,
      "download"
    );
  };
};

const postRecord = (
  dispatch,
  apiUrl,
  data,
  errorMessage,
  rest,
  type = "download"
) => {
  const done = fnDone(rest);
  httpPOSTRequest(apiUrl, data)
    .then((res) => {
      if (res.data && res.data.status) {
        done(null, res.data);
      } else {
        dispatch(serviceActionError(res));
        throw new Error(errorMessage);
      }
    })
    .catch((error) => {
      dispatch(serviceActionError(error));
      dispatch(setFOILoader(false));
    });
};

export const getRecordFormats = (...rest) => {
  const done = fnDone(rest);
  return (dispatch) => {
    httpGETRequest1(FOI_RECORD_FORMATS, null)
      .then((res) => {
        if (res.data) {
          dispatch(
            setRecordFormats([
              ...new Set([
                ...res.data.conversion,
                ...res.data.dedupe,
                ...res.data.nonredactable,
              ]),
            ])
          );
          dispatch(setConversionFormats(res.data.conversion));
        } else {
          console.log("Error in fetching records formats", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        console.log("Error in fetching records formats", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const fetchPDFStitchStatusForRedlines = (
  requestId,
  ministryId,
  ...rest
) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_PDF_STITCH_STATUS_FOR_REDLINES,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setFOIPDFStitchStatusForRedlines(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const fetchPDFStitchedRecordForRedlines = (
  requestId,
  ministryId,
  ...rest
) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_DOWNLOAD_RECORDS_FOR_REDLINES,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setFOIPDFStitchedRecordForRedlines(res.data));
          done(null, res.data);
        } else {
          console.log("Error in fetching records for redlines", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        console.log("Error in fetching records for redlines", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const fetchPDFStitchStatusForResponsePackage = (
  requestId,
  ministryId,
  ...rest
) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_PDF_STITCH_STATUS_FOR_RESPONSEPACKAGE,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setFOIPDFStitchStatusForResponsePackage(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const fetchPDFStitchedRecordForResponsePackage = (
  requestId,
  ministryId,
  ...rest
) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_DOWNLOAD_RECORDS_FOR_RESPONSEPACKAGE,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setFOIPDFStitchedRecordForResponsePackage(res.data));
          done(null, res.data);
        } else {
          console.log("Error in fetching records for response package", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        console.log("Error in fetching records for response package", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};
