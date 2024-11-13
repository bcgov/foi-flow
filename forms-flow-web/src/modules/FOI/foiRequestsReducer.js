import FOI_ACTION_CONSTANTS from "../../actions/FOI/foiActionConstants";
import _ from "lodash";
const initialState = {
  isLoading: true,
  isEventsLoading: true,
  queueFilter: "myRequests",
  queueParams: {
    rowsState: { page: 0, pageSize: 100 },
    sortModel: false,
    keyword: null,
  },
  eventQueueFilter: "myRequests",
  eventQueueParams: {
    rowsState: { page: 0, pageSize: 100 },
    sortModel: false,
    keyword: null,
  },
  showAdvancedSearch: false,
  showEventQueue: false,
  foiAdvancedSearchParams: {},
  isAssignedToListLoading: true,
  isAttachmentListLoading: true,
  isCommentTagListLoading: true,
  foiRequestsList: null,
  foiMinistryRequestsList: [],
  foiEventsList: null,
  foiMinistryEventsList: [],
  foiRequestsCount: 0,
  foiRequestDetail: {},
  foiMinistryViewRequestDetail: {},
  foiIsRequestUpdated: false,
  foiCategoryList: [],
  foiRequestTypeList: [
    { requesttypeid: 0, name: "Select Request Type" },
    { requesttypeid: 1, name: "general" },
    { requesttypeid: 2, name: "personal" },
  ],
  foiReceivedModeList: [],
  foiDeliveryModeList: [],
  foiAssignedToList: [],
  foiProcessingTeamList: [],
  foiFullAssignedToList: [],
  foiMinistryAssignedToList: [],
  foiProgramAreaList: [],
  foiProgramAreaDivisionList: [],
  foiAdminProgramAreaList: [],
  foiRequestDescriptionHistoryList: [],
  foiMinistryDivisionalStages: [],
  foiWatcherList: [],
  foiRequestComments: [],
  foiRequestAttachments: [],
  foiRequestRecords: {
    records: [],
    dedupedfiles: 0,
    removedfiles: 0,
    batchcount: 0,
  },
  foiPDFStitchedRecordForHarms: {},
  foiPDFStitchedRecordForRedlines: {},
  foiPDFStitchedRecordForOipcRedlineReview: {},
  foiPDFStitchedRecordForOipcRedline: {},
  foiPDFStitchedRecordForResponsePackage: {},
  foiPDFStitchStatusForHarms: "not started",
  foiPDFStitchStatusForRedlines: "not started",
  foiPDFStitchStatusForResponsePackage: "not started",
  foiPDFStitchStatusForOipcRedlineReview: "not started",
  foiPDFStitchStatusForOipcRedline: "not started",
  foiRequestCFRForm: {
    overallsuggestions: "",
    status: "init",
    feedata: {
      estimatedtotaldue: 0,
      actualtotaldue: 0,
      actualhardcopypages: 0,
      actualproducinghrs: 0,
      actuallocatinghrs: 0,
      estimatedlocatinghrs: 0,
      estimatedproducinghrs: 0,
      estimatedelectronicpages: 0,
      actualelectronicpages: 0,
      estimatedministrypreparinghrs: 0,
      estimatediaopreparinghrs: 0,
      amountpaid: 0,
      feewaiveramount: 0,
      refundamount: 0,
      estimatedhardcopypages: 0,
      actualministrypreparinghrs: 0,
      actualiaopreparinghrs: 0,
    },
  },
  foiRequestCFRFormHistory: [],
  foiRequestApplicantCorrespondence: [],
  foiRequestApplicantCorrespondenceTemplates: [],
  foiRequestExtesions: [],
  foiOpenedMinistries: [],
  resumeDefaultSorting: false,
  isCorrespondenceLoading: true,
  foiSubjectCodeList: [],
  restrictedReqTaglist: [],
  recordFormats: [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "image/bmp",
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/svg+xml",
    "image/tiff",
    "image/webp",
    "application/vnd.ms-excel.sheet.macroEnabled.12",
    ".msg",
    ".eml",
    ".xls",
    ".xlsx",
    ".doc",
    ".docx",
    ".ics",
    ".json",
    ".shx",
    ".shp",
    ".dbf",
    ".kml",
    ".kmz",
    ".geojson",
    ".cpg",
    ".prj",
    ".sbn",
    ".sbx",
    ".gml",
    ".gdb",
    ".freelist",
    ".atx",
    ".gpkg",
    ".mbtiles",
    ".mpk",
    ".wkt",
    ".las",
    ".lasd",
    ".laz",
    ".dwf",
    ".dwg",
    ".dxf",
    ".csv",
    ".txt",
    ".png",
    ".jpg",
  ],
  conversionFormats: [],
  oipcOutcomes: [],
  oipcStatuses: [],
  oipcReviewtypes: [],
  oipcInquiryoutcomes: [],
  oiExemptions: [],
  oiPublicationStatuses: [],
  oiStatuses: [],
  foiOpenInfoRequest: {},
};

const foiRequests = (state = initialState, action) => {
  switch (action.type) {
    case FOI_ACTION_CONSTANTS.IS_LOADING:
      return { ...state, isLoading: action.payload };
    case FOI_ACTION_CONSTANTS.IS_RECORDS_LOADING:
      return { ...state, isRecordsLoading: action.payload };
    case FOI_ACTION_CONSTANTS.IS_EVENTS_LOADING:
      return { ...state, isEventsLoading: action.payload };
    case FOI_ACTION_CONSTANTS.QUEUE_FILTER:
      return { ...state, queueFilter: action.payload };
    case FOI_ACTION_CONSTANTS.QUEUE_PARAMS:
      return { ...state, queueParams: action.payload };
    case FOI_ACTION_CONSTANTS.EVENT_QUEUE_FILTER:
      return { ...state, eventQueueFilter: action.payload };
    case FOI_ACTION_CONSTANTS.EVENT_QUEUE_PARAMS:
      return { ...state, eventQueueParams: action.payload };
    case FOI_ACTION_CONSTANTS.SHOW_ADVANCED_SEARCH:
      return { ...state, showAdvancedSearch: action.payload };
    case FOI_ACTION_CONSTANTS.SHOW_EVENT_QUEUE:
      return { ...state, showEventQueue: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_ADVANCED_SEARCH_PARAMS:
      return {
        ...state,
        foiAdvancedSearchParams: {
          ...state.foiAdvancedSearchParams,
          ...action.payload,
        },
      };
    case FOI_ACTION_CONSTANTS.IS_ASSIGNEDTOLIST_LOADING:
      return { ...state, isAssignedToListLoading: action.payload };
    case FOI_ACTION_CONSTANTS.IS_ATTACHMENTLIST_LOADING:
      return { ...state, isAttachmentListLoading: action.payload };
    case FOI_ACTION_CONSTANTS.IS_COMMENTTAGLIST_LOADING:
      return { ...state, isCommentTagListLoading: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_LIST_EVENTS:
      return {
        ...state,
        foiEventsList: action.payload,
        isEventsLoading: false,
      };
    case FOI_ACTION_CONSTANTS.FOI_MINISTRY_EVENTLIST:
      return {
        ...state,
        foiMinistryEventsList: action.payload,
        isEventsLoading: false,
      };
    case FOI_ACTION_CONSTANTS.FOI_LIST_REQUESTS:
      return { ...state, foiRequestsList: action.payload, isLoading: false };
    case FOI_ACTION_CONSTANTS.FOI_MINISTRY_REQUESTSLIST:
      return { ...state, foiMinistryRequestsList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUESTS_COUNT:
      return { ...state, foiRequestsCount: action.payload.count };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DETAIL:
      return { ...state, foiRequestDetail: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_APPLICANT_PROFILE:
      return { ...state, foiRequestApplicantProfile: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DUE_DATE:
      return {
        ...state,
        foiRequestDetail: {
          ...state.foiRequestDetail,
          dueDate: action.payload,
        },
      };
    case FOI_ACTION_CONSTANTS.FOI_MINISTRYVIEW_REQUEST_DETAIL:
      return { ...state, foiMinistryViewRequestDetail: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_IS_REQUEST_UPDATED:
      return { ...state, foiIsRequestUpdated: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_CATEGORYLIST:
      return { ...state, foiCategoryList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PROGRAM_AREALIST:
      return { ...state, foiProgramAreaList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PROGRAM_AREA_DIVISIONLIST:
      return { ...state, foiProgramAreaDivisionList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_ADMIN_PROGRAM_AREALIST:
      return { ...state, foiAdminProgramAreaList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_RECEIVED_MODELIST:
      return { ...state, foiReceivedModeList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_DELIVERY_MODELIST:
      return { ...state, foiDeliveryModeList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_ASSIGNED_TOLIST:
      return { ...state, foiAssignedToList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PROCESSING_TEAM_LIST:
      return { ...state, foiProcessingTeamList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_FULL_ASSIGNED_TOLIST:
      return { ...state, foiFullAssignedToList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_MINISTRY_ASSIGNED_TOLIST:
      return { ...state, foiMinistryAssignedToList: action.payload };
    case FOI_ACTION_CONSTANTS.CLEAR_REQUEST_DETAILS:
      return { ...state, foiRequestDetail: action.payload };
    case FOI_ACTION_CONSTANTS.CLEAR_MINISTRYVIEWREQUEST_DETAILS:
      return { ...state, foiMinistryViewRequestDetail: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DESCRIPTION_HISTORY:
      return { ...state, foiRequestDescriptionHistoryList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_MINISTRY_DIVISIONALSTAGES:
      return { ...state, foiMinistryDivisionalStages: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PERSONAL_DIVISIONS_SECTIONS:
      return { ...state, foiPersonalDivisionsAndSections: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PERSONAL_SECTIONS:
      return { ...state, foiPersonalSections: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PERSONAL_PEOPLE:
      return { ...state, foiPersonalPeople: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PERSONAL_FILETYPES:
      return { ...state, foiPersonalFiletypes: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PERSONAL_VOLUMES:
      return { ...state, foiPersonalVolumes: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_WATCHER_LIST:
      return { ...state, foiWatcherList: action.payload };
    case FOI_ACTION_CONSTANTS.CLOSING_REASONS:
      return { ...state, closingReasons: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_COMMENTS:
      return { ...state, foiRequestComments: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_ATTACHMENTS:
      return { ...state, foiRequestAttachments: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_RECORDS:
      return { ...state, foiRequestRecords: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_HARMS:
      return { ...state, foiPDFStitchedRecordForHarms: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_REDLINES:
      return { ...state, foiPDFStitchedRecordForRedlines: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_RESPONSEPACKAGE:
      return {
        ...state,
        foiPDFStitchedRecordForResponsePackage: action.payload,
      };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_OIPCREDLINEREVIEW:
      return {
        ...state,
        foiPDFStitchedRecordForOipcRedlineReview: action.payload,
      };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_RECORD_FOR_OIPCREDLINE:
      return {
        ...state,
        foiPDFStitchedRecordForOipcRedline: action.payload,
      };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_HARMS:
      return { ...state, foiPDFStitchStatusForHarms: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_REDLINES:
      return { ...state, foiPDFStitchStatusForRedlines: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_RESPONSEPACKAGE:
      return { ...state, foiPDFStitchStatusForResponsePackage: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_OIPCREDLINEREVIEW:
      return { ...state, foiPDFStitchStatusForOipcRedlineReview: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_PDF_STITCHED_STATUS_FOR_OIPCREDLINE:
      return { ...state, foiPDFStitchStatusForOipcRedline: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_CFR_FORM:
      return {
        ...state,
        foiRequestCFRForm: _.isEmpty(action.payload)
          ? initialState.foiRequestCFRForm
          : {
              ...state.foiRequestCFRForm,
              ...action.payload,
            },
      };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_CFR_FORM_HISTORY:
      return { ...state, foiRequestCFRFormHistory: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_APPLICANT_CORRESPONDENCE:
      return { ...state, foiRequestApplicantCorrespondence: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_APPLICANT_CORRESPONDENCE_TEMPLATES:
      return {
        ...state,
        foiRequestApplicantCorrespondenceTemplates: action.payload,
      };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_EXTENSIONS:
      return { ...state, foiRequestExtesions: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_OPENED_MINISTRIES:
      return { ...state, foiOpenedMinistries: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_AXIS_REQUEST_IDS:
      return { ...state, foiAxisRequestIds: action.payload };
    case FOI_ACTION_CONSTANTS.RESUME_DEFAULT_SORTING:
      return { ...state, resumeDefaultSorting: action.payload };
    case FOI_ACTION_CONSTANTS.IS_CORRESPONDENCE_LOADING:
      return { ...state, isCorrespondenceLoading: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_SUBJECT_CODELIST:
      return { ...state, foiSubjectCodeList: action.payload };
    case FOI_ACTION_CONSTANTS.RESTRICTED_COMMENT_TAG_LIST:
      return { ...state, restrictedReqTaglist: action.payload };
    case FOI_ACTION_CONSTANTS.RECORD_FORMATS:
      return { ...state, recordFormats: action.payload };
    case FOI_ACTION_CONSTANTS.CONVERSION_FORMATS:
      return { ...state, conversionFormats: action.payload };
    case FOI_ACTION_CONSTANTS.OIPC_OUTCOMES:
      return { ...state, oipcOutcomes: action.payload };
    case FOI_ACTION_CONSTANTS.OIPC_STATUSES:
      return { ...state, oipcStatuses: action.payload };
    case FOI_ACTION_CONSTANTS.OIPC_REVIEWTYPES:
      return { ...state, oipcReviewtypes: action.payload };
    case FOI_ACTION_CONSTANTS.OIPC_INQUIRYOUTCOMES:
        return { ...state, oipcInquiryoutcomes: action.payload };
    case FOI_ACTION_CONSTANTS.OI_EXEMPTIONS:
      return { ...state, oiExemptions: action.payload };
    case FOI_ACTION_CONSTANTS.OI_PUBLICATIONSTATUSES:
      return { ...state, oiPublicationStatuses: action.payload };
    case FOI_ACTION_CONSTANTS.OI_STATUSES:
      return { ...state, oiStatuses: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_OPENINFO_REQUEST:
      return {...state, foiOpenInfoRequest: action.payload}
    default:
      return state;
  }
};
export default foiRequests;
