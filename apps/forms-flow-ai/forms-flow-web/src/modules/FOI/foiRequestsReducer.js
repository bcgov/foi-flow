import FOI_ACTION_CONSTANTS from "../../actions/FOI/foiActionConstants";

const initialState = {
  isLoading:true,
  isAssignedToListLoading:true,
  foiRequestsList:[],
  foiMinistryRequestsList:[],
  foiRequestsCount:0,
  foiRequestDetail: {},
  foiMinistryViewRequestDetail:{},
  foiIsRequestUpdated:false,
  foiCategoryList: [], 
  foiRequestTypeList:[{"requesttypeid":0, "name": "Select Request Type"}, {"requesttypeid":1, "name": "general"}, {"requesttypeid":2, "name": "personal"}],
  foiReceivedModeList:[],
  foiDeliveryModeList:[],
  foiAssignedToList: [],
  foiFullAssignedToList: [],
  foiMinistryAssignedToList: [],
  foiProgramAreaList:[],
  foiRequestDescriptionHistoryList: [], 
  foiMinistryDivisionalStages:[], 
  foiWatcherList: [],
  foiRequestComments:[]
}


const foiRequests = (state = initialState, action)=> {  
  switch (action.type) {
    case FOI_ACTION_CONSTANTS.IS_LOADING:
      return {...state, isLoading: action.payload};
    case FOI_ACTION_CONSTANTS.IS_ASSIGNEDTOLIST_LOADING:
      return {...state, isAssignedToListLoading: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_LIST_REQUESTS:
      return {...state, foiRequestsList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_MINISTRY_REQUESTSLIST:
      return {...state, foiMinistryRequestsList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_REQUESTS_COUNT:
      return {...state, foiRequestsCount: action.payload.count};
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DETAIL:      
      return {...state, foiRequestDetail: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_MINISTRYVIEW_REQUEST_DETAIL:      
      return {...state, foiMinistryViewRequestDetail: action.payload};  
    case FOI_ACTION_CONSTANTS.FOI_IS_REQUEST_UPDATED:
      return {...state, foiIsRequestUpdated: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_CATEGORYLIST:
        return {...state, foiCategoryList: action.payload};   
    case FOI_ACTION_CONSTANTS.FOI_SELECTED_CATEGORY:
      return {...state, foiSelectedCategory: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_PROGRAM_AREALIST:
      return {...state, foiProgramAreaList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_IS_REQUIRED_ERROR:
      return {...state, foiIsRequiredError: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_REQUIRED_FIELDS:
      const requiredFields = state.foirequiredFields;
      requiredFields[action.payload.property] = action.payload.value;
      return {...state, foirequiredFields: requiredFields};
    case FOI_ACTION_CONSTANTS.FOI_SELECTED_ASSIGNED_TO:
      return {...state, foiSelectedAssignedTo: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_SELECTED_REQUEST_TYPE:
      return {...state, foiSelectedRequestType: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_SELECTED_RECEIVED_MODE:
      return {...state, foiSelectedReceiveMode: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_SELECTED_DELIVERY_MODE:
      return {...state, foiSelectedDeliveryMode: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DESCRIPTION:
      return {...state, foiRequestDescription: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_START_DATE:
      return {...state, foiStartDate: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_END_DATE:
      return {...state, foiEndDate: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_RECEIVED_DATE:
      return {...state, foiReceivedDate: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_START_DATE:
      return {...state, foiRequestStartDate: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_IS_MINISTRY_SELECTED:
      return {...state, foiIsMinistrySelected: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_RECEIVED_MODELIST:
        return {...state, foiReceivedModeList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_DELIVERY_MODELIST:
        return {...state, foiDeliveryModeList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_ASSIGNED_TOLIST:
        return {...state, foiAssignedToList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_FULL_ASSIGNED_TOLIST:
        return {...state, foiFullAssignedToList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_MINISTRY_ASSIGNED_TOLIST:
        return {...state, foiMinistryAssignedToList: action.payload};
    case FOI_ACTION_CONSTANTS.CLEAR_REQUEST_DETAILS:
      return {...state, foiRequestDetail: action.payload};
    case FOI_ACTION_CONSTANTS.CLEAR_MINISTRYVIEWREQUEST_DETAILS:
      return {...state, foiMinistryViewRequestDetail: action.payload};  
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DESCRIPTION_HISTORY:
      return {...state, foiRequestDescriptionHistoryList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_MINISTRY_DIVISIONALSTAGES:
      return {...state, foiMinistryDivisionalStages: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_WATCHER_LIST:
      return {...state, foiWatcherList: action.payload};
    case FOI_ACTION_CONSTANTS.CLOSING_REASONS:
      return {...state, closingReasons: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_COMMENTS:
      return {...state, foiRequestComments: action.payload};
    default:
      return state;
  }
}

export default foiRequests ;
