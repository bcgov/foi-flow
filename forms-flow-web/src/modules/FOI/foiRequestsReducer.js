import FOI_ACTION_CONSTANTS from "../../actions/FOI/foiActionConstants";
import _ from 'lodash';
const initialState = {
  isLoading: true,
  queueFilter: "myRequests",
  queueParams: {
    rowsState: { page: 0, pageSize: 100 },
    sortModel: false,
    keyword: null,
  },
  showAdvancedSearch: false,
  foiAdvancedSearchParams: {},
  isAssignedToListLoading: true,
  isAttachmentListLoading: true,
  foiRequestsList: null,
  foiMinistryRequestsList: [],
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
  foiRequestDescriptionHistoryList: [],
  foiMinistryDivisionalStages: [],
  foiWatcherList: [],
  foiRequestComments: [],
  foiRequestAttachments: [],
  foiRequestCFRForm: {
    overallsuggestions: "",
    status: "init",
    feedata: {
       totalamountdue: 0,
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
       estimatedhardcopypages: 0,
       actualministrypreparinghrs: 0,
       actualiaopreparinghrs: 0,
    }
  },
  foiRequestCFRFormHistory: [],
  foiRequestExtesions: [],
  foiOpenedMinistries: [],
  resumeDefaultSorting: false,
};

const foiRequests = (state = initialState, action) => {
  switch (action.type) {
    case FOI_ACTION_CONSTANTS.IS_LOADING:
      return { ...state, isLoading: action.payload };
    case FOI_ACTION_CONSTANTS.QUEUE_FILTER:
      return { ...state, queueFilter: action.payload };
      case FOI_ACTION_CONSTANTS.QUEUE_PARAMS:
        return { ...state, queueParams: action.payload };
    case FOI_ACTION_CONSTANTS.SHOW_ADVANCED_SEARCH:
      return { ...state, showAdvancedSearch: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_ADVANCED_SEARCH_PARAMS:
      return { 
        ...state, 
        foiAdvancedSearchParams: {
          ...state.foiAdvancedSearchParams,
          ...action.payload 
        }
      };
    case FOI_ACTION_CONSTANTS.IS_ASSIGNEDTOLIST_LOADING:
      return { ...state, isAssignedToListLoading: action.payload };
    case FOI_ACTION_CONSTANTS.IS_ATTACHMENTLIST_LOADING:
      return { ...state, isAttachmentListLoading: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_LIST_REQUESTS:
      return { ...state, foiRequestsList: action.payload, isLoading: false };
    case FOI_ACTION_CONSTANTS.FOI_MINISTRY_REQUESTSLIST:
      return { ...state, foiMinistryRequestsList: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUESTS_COUNT:
      return { ...state, foiRequestsCount: action.payload.count };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DETAIL:
      return { ...state, foiRequestDetail: action.payload };
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
    case FOI_ACTION_CONSTANTS.FOI_WATCHER_LIST:
      return { ...state, foiWatcherList: action.payload };
    case FOI_ACTION_CONSTANTS.CLOSING_REASONS:
      return { ...state, closingReasons: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_COMMENTS:
      return { ...state, foiRequestComments: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_ATTACHMENTS:
      return { ...state, foiRequestAttachments: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_CFR_FORM:
      return {
        ...state,
        foiRequestCFRForm: _.isEmpty(action.payload) ? initialState.foiRequestCFRForm : {
          ...state.foiRequestCFRForm,
          ...action.payload
        }
      };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_CFR_FORM_HISTORY:
      return { ...state, foiRequestCFRFormHistory: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_EXTENSIONS:
      return { ...state, foiRequestExtesions: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_OPENED_MINISTRIES:
      return { ...state, foiOpenedMinistries: action.payload };
    case FOI_ACTION_CONSTANTS.FOI_AXIS_REQUEST_IDS:
      return { ...state, foiAxisRequestIds: action.payload };
    case FOI_ACTION_CONSTANTS.RESUME_DEFAULT_SORTING:
      return { ...state, resumeDefaultSorting: action.payload };
    default:
      return state;
  }
};
export default foiRequests ;
