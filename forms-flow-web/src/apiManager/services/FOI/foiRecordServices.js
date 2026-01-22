import {
  httpDELETERequest,
  httpGETRequest,
  httpGETRequest1,
  httpPOSTRequest, httpPUTRequest,
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
  setFOIPDFStitchedRecordForOipcRedlineReview,
  setFOIPDFStitchStatusForOipcRedlineReview,
  setFOIPDFStitchStatusForOipcRedline,
  setFOIPDFStitchedRecordForOipcRedline,
  setRequestAttachments,
  setFOIAttachmentListLoader,
  setFOIPDFStitchStatusForConsults,
  setFOIPDFStitchedRecordForConsults,
  setFOIPDFStitchStatusesForPhasedRedlines,
  setFOIPDFStitchedRecordsForPhasedRedlines,
  setFOIPDFStitchStatusesForPhasedResponsePackages,
  setFOIPDFStitchedRecordsForPhasedResponsePackages
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

// Helper function (assuming you can refactor or create this)
// const replaceUrl = (url, placeholder, value) => url.replace(placeholder, value);

export const fetchFOIRecords = (requestId, ministryId) => async (dispatch) => {
  // 1. Cleaner Early Exit
  if (!ministryId) {
    console.warn("Cannot fetch records: ministryId is missing.");
    return;
  }

  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_GET_RECORDS, "<ministryrequestid>", ministryId),
    "<requestid>",
    requestId
  );

  // 2. Start Loading
  dispatch(setRecordsLoader("inprogress"));

  try {
    // 3. Await the API call for linear reading
    const res = await httpGETRequest(apiUrl, {}, UserService.getToken());

    if (res.data) {
      // 4. Success
      dispatch(setRequestRecords(res.data));
      dispatch(setRecordsLoader("completed"));

      // Removed the 'done' callback pattern for simplicity,
      // relying on the caller to handle the promise or thunk result if needed.
      return res.data;

    } else {
      // API call succeeded but returned unexpected data
      console.error("API returned incomplete data for records:", res);
      dispatch(serviceActionError(res));
      dispatch(setRecordsLoader("error"));
      // Throw error to be caught by the outer catch block if necessary, or just log
    }

  } catch (error) {
    // 5. Catch API Failure
    console.error("Error in fetching FOI records:", error);
    dispatch(serviceActionError(error));
    dispatch(setRecordsLoader("error"));
  }
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
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          console.log("Error in fetching redacted sections", res);
          dispatch(serviceActionError(res));
        }
      })
      .catch((error) => {
        console.log("Error in fetching redacted section", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const fetchDocumentPage  = (ministryId, done) => {
  if (!ministryId) {
    return (dispatch) => {};
  }

  let apiUrl = replaceUrl(
    API.DOC_REVIEWER_REDACTED_DOCUMENT_RECORDS,
    "<ministryrequestid>",
    ministryId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          console.log("Error in fetching redacted sections", res);
          serviceActionError(res)(dispatch);
        }
      })
      .catch((error) => {
        console.log("Error in fetching redacted section", error);
        serviceActionError(error)(dispatch);
        done(error);
      });
  };
};

export const fetchDocumentPageFlags  = (ministryId, done) => {
  if (!ministryId) {
    return (dispatch) => {};
  }

  let apiUrl = replaceUrl(
    API.DOC_REVIEWER_REDACTED_PAGEFLAG_RECORDS,
    "<ministryrequestid>",
    ministryId
  );
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          console.log("Error in fetching redacted sections", res);
          serviceActionError(res)(dispatch);
        }
      })
      .catch((error) => {
        console.log("Error in fetching redacted section", error);
        serviceActionError(error)(dispatch);
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

export const editPersonalAttributes = (requestId, ministryId, data, ...rest) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_UPDATE_PERSONAL_ATTRIBUTES, "<ministryrequestid>", ministryId),
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

export const fetchPDFStitchStatusesForPhasedRedlines = (
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
      API.FOI_PDF_STITCH_STATUSES_FOR_PHASEDREDLINES,
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
          dispatch(setFOIPDFStitchStatusesForPhasedRedlines(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
}

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

export const fetchPDFStitchStatusesForPhasedResponsePackages = (
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
      API.FOI_PDF_STITCH_STATUSES_FOR_PHASEDRESPONSEPACKAGES,
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
          dispatch(setFOIPDFStitchStatusesForPhasedResponsePackages(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
}

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

export const fetchPDFStitchedStatus = (
  requestId,
  ministryId,
  packagename,
  ...rest) => {
    if (!ministryId) {
      return () => {};
    }
    const done = fnDone(rest);
    let apiUrl = replaceUrl(replaceUrl(
      replaceUrl(
        API.FOI_PDF_STITCH_STATUS,
        "<ministryrequestid>",
        ministryId
      ),
      "<requestid>",
      requestId
    ), '<packagename>', packagename);
    return (dispatch) => {
      httpGETRequest(apiUrl, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            done(null, res.data);
          }
        })
        .catch((error) => {
          console.log("Error in fetching pdfstitch job status", error);
          dispatch(serviceActionError(error));
          done(error);
        });
    };
  }

export const fetchPDFStitchedPackage = (
  requestId,
  ministryId,
  packagename,
  ...rest
) => {
  if (!ministryId) {
    return () => {};
  }
  const done = fnDone(rest);
  let apiUrl = replaceUrl(
    replaceUrl(
      API.FOI_DOWNLOAD_ZIPPED_PACKAGE,
      "<ministryrequestid>",
      ministryId
    ),
    "<requestid>",
    requestId
  ) + "/" + packagename;
  return (dispatch) => {
    httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
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

export const fetchPDFStitchedRecordsForPhasedResponsePackages = (
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
      API.FOI_DOWNLOAD_RECORDS_FOR_PHASEDRESPONSEPACKAGES,
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
          dispatch(setFOIPDFStitchedRecordsForPhasedResponsePackages(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
}

export const fetchPDFStitchedStatusForOIPCRedline = (
  requestId,
  ministryId,
  ...rest) => {
    if (!ministryId) {
      return () => {};
    }
    const done = fnDone(rest);
    let apiUrl = replaceUrl(
      replaceUrl(
        API.FOI_PDF_STITCH_STATUS_FOR_OIPCREDLINE,
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
            dispatch(setFOIPDFStitchStatusForOipcRedline(res.data));
            done(null, res.data);
          }
        })
        .catch((error) => {
          console.log("Error in fetching pdfstitch job status", error);
          dispatch(serviceActionError(error));
          done(error);
        });
    };
  }

export const fetchPDFStitchedRecordForOIPCRedline = (
  requestId,
  ministryId,
  ...rest) => {
    if (!ministryId) {
      return () => {};
    }
    const done = fnDone(rest);
    let apiUrl = replaceUrl(
      replaceUrl(
        API.FOI_DOWNLOAD_RECORDS_FOR_OIPCREDLINE,
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
            dispatch(setFOIPDFStitchedRecordForOipcRedline(res.data));
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
  }

export const fetchPDFStitchedStatusForOIPCRedlineReview = (
  requestId,
  ministryId,
  ...rest) => {
    if (!ministryId) {
      return () => {};
    }
    const done = fnDone(rest);
    let apiUrl = replaceUrl(
      replaceUrl(
        API.FOI_PDF_STITCH_STATUS_FOR_OIPCREDLINEREVIEW,
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
            dispatch(setFOIPDFStitchStatusForOipcRedlineReview(res.data));
            done(null, res.data);
          }
        })
        .catch((error) => {
          console.log("Error in fetching pdfstitch job status", error);
          dispatch(serviceActionError(error));
          done(error);
        });
    };
  }

export const fetchPDFStitchedRecordForOIPCRedlineReview = (
  requestId,
  ministryId,
  ...rest) => {
    if (!ministryId) {
      return () => {};
    }
    const done = fnDone(rest);
    let apiUrl = replaceUrl(
      replaceUrl(
        API.FOI_DOWNLOAD_RECORDS_FOR_OIPCREDLINEREVIEW,
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
            dispatch(setFOIPDFStitchedRecordForOipcRedlineReview(res.data));
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
  }

  export const fetchHistoricalRecords = (axisRequestId, ...rest) => {
    const done = fnDone(rest);
    let apiUrl = replaceUrl(API.FOI_HISTORICAL_RECORDS_API, "<axisrequestid>", axisRequestId);
    return (dispatch) => {
      dispatch(setRecordsLoader("inprogress"));
      httpGETRequest(apiUrl, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            if (!res.data.records) {
              dispatch(setRequestAttachments(res.data));
              dispatch(setFOIAttachmentListLoader(false));
            } else {
              dispatch(setRequestRecords(res.data));
              dispatch(setRecordsLoader("completed"));
            }
            done(null, res.data);
          } else {
            console.log("Error in fetching historical records", res);
            dispatch(serviceActionError(res));
            dispatch(setRecordsLoader("error"));
          }
        })
        .catch((error) => {
          console.log("Error in fetching historical records", error);
          dispatch(serviceActionError(error));
          dispatch(setRecordsLoader("error"));
          done(error);
        });
    };
  };


export const fetchPDFStitchStatusForConsults = (
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
      API.FOI_PDF_STITCH_STATUS_FOR_CONSULTPACKAGE,
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
          dispatch(setFOIPDFStitchStatusForConsults(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
}

export const fetchPDFStitchedRecordForConsults = (
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
      API.FOI_DOWNLOAD_RECORDS_FOR_CONSULTPACKAGE,
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
          dispatch(setFOIPDFStitchedRecordForConsults(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
}

export const fetchPDFStitchedRecordsForPhasedRedlines = (
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
      API.FOI_DOWNLOAD_RECORDS_FOR_PHASEDREDLINES,
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
          dispatch(setFOIPDFStitchedRecordsForPhasedRedlines(res.data));
          done(null, res.data);
        }
      })
      .catch((error) => {
        console.log("Error in fetching pdfstitch job status", error);
        dispatch(serviceActionError(error));
        done(error);
      });
  };
}

export const updateUserLockedRecords = (data, requestId, ministryId, ...rest) => {
  const done = fnDone(rest);
  let apiUrl= replaceUrl(replaceUrl(
    API.FOI_REQUEST_SECTION_API,
    "<ministryid>",
    ministryId),"<requestid>",requestId
  );
  return (dispatch) => {
    httpPOSTRequest(`${apiUrl}/userrecordslockstatus`, data)
      .then((res) => {
        if (res.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error while updating records lock status for the (request# ${requestId}, ministry# ${ministryId})`);
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(error);
      });
  };
}

export const retrieveSelectedRecordVersion = (
  requestId,
  ministryId,
  data,
  ...rest
) => {
  let apiUrl = replaceUrl(
    replaceUrl(API.FOI_RETRIEVE_RECORDS, "<ministryrequestid>", ministryId),
    "<requestid>",
    requestId
  );
  return (dispatch) => {
    const done = fnDone(rest);
    httpPOSTRequest(apiUrl, data)
      .then((res) => {
        if (res.data && res.data.status) {
          dispatch(setFOIPDFStitchStatusForHarms("not started"));
          dispatch(fetchFOIRecords(requestId, ministryId));
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error in retrieving uncompressed files");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
      });
  };
};


export const createFOIRecordGroup = (
  requestId,
  ministryId,
  data,
  done
) => {
  let apiUrl = API.FOI_POST_RECORD_GROUP;
  apiUrl = replaceUrl(apiUrl, "<requestid>", requestId);
  apiUrl = replaceUrl(apiUrl, "<ministryrequestid>", ministryId);

  return (dispatch) => {
    httpPOSTRequest(apiUrl, data, UserService.getToken())
      .then((res) => {
        if (res?.data) {
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          done("Error saving record group");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};


export const updateFOIRecordGroup = (
  requestId,
  ministryId,
  groupId,
  data,
  done
) => {

  let apiUrl = API.FOI_PUT_RECORD_GROUP;
  apiUrl = replaceUrl(apiUrl, "<requestid>", requestId);
  apiUrl = replaceUrl(apiUrl, "<ministryrequestid>", ministryId);
  apiUrl = replaceUrl(apiUrl, "<groupid>", groupId);

  return (dispatch) => {
    httpPUTRequest(apiUrl, data, UserService.getToken())
      .then((res) => {
        const payload = res?.data;
        if (payload) {
          done(null, payload);
        } else {
          dispatch(serviceActionError(res));
          done("Error updating record group");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};

export const deleteFOIRecordFromGroup = (
  requestId,
  ministryId,
  groupId,
  recordId,
  done
) => {
  let apiUrl = API.FOI_DELETE_RECORD_GROUP;
  apiUrl = replaceUrl(apiUrl, "<requestid>", requestId);
  apiUrl = replaceUrl(apiUrl, "<ministryrequestid>", ministryId);
  apiUrl = replaceUrl(apiUrl, "<groupid>", groupId);
  apiUrl = replaceUrl(apiUrl, "<recordid>", recordId);

  return (dispatch) => {
    httpDELETERequest(apiUrl, UserService.getToken())
      .then((res) => {
        const payload = res?.data;
        if (payload) {
          done(null, payload);
        } else {
          dispatch(serviceActionError(res));
          done("Error deleting record from document set");
        }
      })
      .catch((error) => {
        dispatch(serviceActionError(error));
        done(error);
      });
  };
};


export const getFOIRecordGroup = async (requestId, ministryId) => {
  let apiUrl = API.FOI_GET_RECORD_GROUP;
  apiUrl = replaceUrl(apiUrl, "<requestid>", requestId);
  apiUrl = replaceUrl(apiUrl, "<ministryrequestid>", ministryId);

  const res = await httpGETRequest(apiUrl, null, UserService.getToken());
  return res?.data?.data || [];
};
