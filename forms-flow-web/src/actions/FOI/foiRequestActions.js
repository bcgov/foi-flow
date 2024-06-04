import FOI_ACTION_CONSTANTS from "./foiActionConstants";

export const setFOILoader = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.IS_LOADING,
    payload: data,
  });
};

export const setRecordsLoader = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.IS_RECORDS_LOADING,
    payload: data,
  });
};
export const setFOIEventsLoader = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.IS_EVENTS_LOADING,
    payload: data,
  });
};

export const setQueueFilter = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.QUEUE_FILTER,
    payload: data,
  });
};
export const setQueueParams = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.QUEUE_PARAMS,
    payload: data,
  });
};
export const setEventQueueFilter = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.EVENT_QUEUE_FILTER,
    payload: data,
  });
};
export const setEventQueueParams = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.EVENT_QUEUE_PARAMS,
    payload: data,
  });
};
export const setShowEventQueue = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.SHOW_EVENT_QUEUE,
    payload: data,
  });
};
export const setShowAdvancedSearch = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.SHOW_ADVANCED_SEARCH,
    payload: data,
  });
};
export const setAdvancedSearchParams = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_ADVANCED_SEARCH_PARAMS,
    payload: data,
  });
};
export const setFOIAssignedToListLoader = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.IS_ASSIGNEDTOLIST_LOADING,
    payload: data,
  });
};
export const setFOIAttachmentListLoader = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.IS_ATTACHMENTLIST_LOADING,
    payload: data,
  });
};
export const setCommentTagListLoader = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.IS_COMMENTTAGLIST_LOADING,
    payload: data,
  });
};
export const setFOIUpdateLoader = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_IS_REQUEST_UPDATED,
    payload: data,
  });
};
export const setFOIEventList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_LIST_EVENTS,
    payload: data,
  });
};
export const setFOIMinistryEventList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_MINISTRY_EVENTLIST,
    payload: data,
  });
};
export const setFOIRequestList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_LIST_REQUESTS,
    payload: data,
  });
};
export const setFOIMinistryRequestList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_MINISTRY_REQUESTSLIST,
    payload: data,
  });
};
export const setFOIRequestCount = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUESTS_COUNT,
    payload: data,
  });
};
export const setFOIRequestDetail = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_DETAIL,
    payload: data,
  });
};
export const setFOIMinistryViewRequestDetail = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_MINISTRYVIEW_REQUEST_DETAIL,
    payload: data,
  });
};
export const setFOIPDFStitchedRecordForHarms = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_HARMS,
    payload: data,
  });
};
export const setFOIPDFStitchedRecordForRedlines = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_REDLINES,
    payload: data,
  });
};
export const setFOIPDFStitchedRecordForResponsePackage =
  (data) => (dispatch) => {
    dispatch({
      type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_RESPONSEPACKAGE,
      payload: data,
    });
  };
export const setFOIPDFStitchedRecordForOipcRedlineReview = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_OIPCREDLINEREVIEW,
    payload: data,
  });
}
export const setFOIPDFStitchedRecordForOipcRedline = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_OIPCREDLINE,
    payload: data,
  });
}
export const setFOIPDFStitchStatusForHarms = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_HARMS,
    payload: data,
  });
};

export const setFOIPDFStitchStatusForRedlines = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_REDLINES,
    payload: data,
  });
};
export const setFOIPDFStitchStatusForResponsePackage = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_RESPONSEPACKAGE,
    payload: data,
  });
};
export const setFOIPDFStitchStatusForOipcRedlineReview = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_OIPCREDLINEREVIEW,
    payload: data,
  });
};
export const setFOIPDFStitchStatusForOipcRedline = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_OIPCREDLINE,
    payload: data,
  });
};

export const serviceActionError = (_data) => (dispatch) => {
  //TODO update to a common file
  dispatch({
    type: FOI_ACTION_CONSTANTS.ERROR,
    payload: "Error Handling API",
  });
};
export const setFOICategoryList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_CATEGORYLIST,
    payload: data,
  });
};
export const setFOICountryList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_COUNTRYLIST,
    payload: data,
  });
};
export const setFOIProvinceList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PROVINCELIST,
    payload: data,
  });
};
export const setFOIRequestTypeList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_TYPELIST,
    payload: data,
  });
};
export const setFOIReceivedModeList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_RECEIVED_MODELIST,
    payload: data,
  });
};
export const setFOIDeliveryModeList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_DELIVERY_MODELIST,
    payload: data,
  });
};
export const setFOIAssignedToList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_ASSIGNED_TOLIST,
    payload: data,
  });
};

export const setFOIProcessingTeamList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PROCESSING_TEAM_LIST,
    payload: data,
  });
};

export const setFOIFullAssignedToList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_FULL_ASSIGNED_TOLIST,
    payload: data,
  });
};
export const setFOIMinistryAssignedToList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_MINISTRY_ASSIGNED_TOLIST,
    payload: data,
  });
};
export const setFOIProgramAreaList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PROGRAM_AREALIST,
    payload: data,
  });
};
export const setFOIProgramAreaDivisionsList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_PROGRAM_AREA_DIVISIONLIST,
    payload: data,
  });
};
export const setFOIAdminProgramAreaList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_ADMIN_PROGRAM_AREALIST,
    payload: data,
  });
};
export const clearRequestDetails = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.CLEAR_REQUEST_DETAILS,
    payload: data,
  });
};

export const clearMinistryViewRequestDetails = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.CLEAR_MINISTRYVIEWREQUEST_DETAILS,
    payload: data,
  });
};
export const setFOIRequestDescriptionHistory = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_DESCRIPTION_HISTORY,
    payload: data,
  });
};
export const setFOIMinistryDivisionalStages = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_MINISTRY_DIVISIONALSTAGES,
    payload: data,
  });
};
export const setFOIPersonalDivisionsAndSections = (data) => dispatch => {
  dispatch({
      type:FOI_ACTION_CONSTANTS.FOI_PERSONAL_DIVISIONS_SECTIONS,
      payload:data      
  })
}
export const setFOIPersonalSections = (data) => dispatch => {
  dispatch({
      type:FOI_ACTION_CONSTANTS.FOI_PERSONAL_SECTIONS,
      payload:data      
  })
}
export const setFOIWatcherList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_WATCHER_LIST,
    payload: data,
  });
};
export const setClosingReasons = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.CLOSING_REASONS,
    payload: data,
  });
};
export const clearRawRequestComments = (_data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_RAWREQUEST_COMMENTS,
    payload: {},
  });
};
export const setRequestComments = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_COMMENTS,
    payload: data,
  });
};
export const setRequestAttachments = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_ATTACHMENTS,
    payload: data,
  });
};
export const setRequestCFRForm = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_CFR_FORM,
    payload: data,
  });
};

export const setRequestCFRFormHistory = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_CFR_FORM_HISTORY,
    payload: data,
  });
};

export const setApplicantCorrespondence = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_APPLICANT_CORRESPONDENCE,
    payload: data,
  });
};

export const setApplicantCorrespondenceTemplates = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_APPLICANT_CORRESPONDENCE_TEMPLATES,
    payload: data,
  });
};

export const setRequestExtensions = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_EXTENSIONS,
    payload: data,
  });
};

export const setRequestRecords = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_RECORDS,
    payload: data,
  });
};

export const setOpenedMinistries = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_OPENED_MINISTRIES,
    payload: data,
  });
};

export const setExistingAxisRequestIds = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_AXIS_REQUEST_IDS,
    payload: data,
  });
};

export const setRequestDueDate = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_REQUEST_DUE_DATE,
    payload: data,
  });
};

export const setResumeDefaultSorting = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.RESUME_DEFAULT_SORTING,
    payload: data,
  });
};

export const setFOICorrespondenceLoader = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.IS_CORRESPONDENCE_LOADING,
    payload: data,
  });
};

export const setFOISubjectCodeList = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_SUBJECT_CODELIST,
    payload: data,
  });
};

export const setRestrictedReqTaglist = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.RESTRICTED_COMMENT_TAG_LIST,
    payload: data,
  });
};

export const setRecordFormats = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.RECORD_FORMATS,
    payload: data,
  });
};

export const setConversionFormats = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.CONVERSION_FORMATS,
    payload: data,
  });
};

export const setOIPCOutcomes = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.OIPC_OUTCOMES,
    payload: data,
  });
};

export const setOIPCStatuses = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.OIPC_STATUSES,
    payload: data,
  });
};

export const setOIPCReviewtypes = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.OIPC_REVIEWTYPES,
    payload: data,
  });
};

export const setOIPCInquiryoutcomes = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.OIPC_INQUIRYOUTCOMES,
    payload: data,
  });
};

export const setAdvancedSearchFilter = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_ADVANCED_SEARCH_FILTER,
    payload: data,
  });
};

export const setHistoricalSearchParams = (data) => (dispatch) => {
  dispatch({
    type: FOI_ACTION_CONSTANTS.FOI_HISTORIC_SEARCH_PARAMS,
    payload: data,
  });
};