import FOI_ACTION_CONSTANTS from "../../actions/FOI/foiActionConstants";
import { formatDate } from "../../helper/helper";

const initialState = {
  isLoading:true,
  foiRequestsList:[],
  foiRequestsCount:0,
  foiRequestDetail: {},
  foiIsRequestUpdating:false,
  foiCategoryList: [],
  foiSelectedCategory: "",
  foiCountryList: [{"countryid":0, "name": "Select Country"},{"countryid":1, "name": "Canada"}],
  foiProvinceList: [{"provinceid":0, "name": "Select Province"},{"provinceid":1, "name": "British Columbia"}, {"provinceid":2, "name": "Ontario"}],
  foiRequestTypeList:[{"requesttypeid":0, "name": "Select Request Type"}, {"requesttypeid":1, "name": "general"}, {"requesttypeid":2, "name": "personal"}],
  foiReceiveModeList:[{"receivemodeid":0, "name": "Select Received Mode"}, {"receivemodeid":1, "name": "Mode1"}, {"receivemodeid":2, "name": "Mode2"}],
  foiDeliveryModeList:[{"deliverymodeid":0, "name": "Select Delivery Mode"}, {"deliverymodeid":1, "name": "Mode1"}, {"deliverymodeid":2, "name": "Mode2"}],
  foiAssignedToList: [{"id":0, "name": "Unassigned"}, {"id":1, "name": "UserName1"}, {"id":2, "name": "UserName2"}, {"id":3, "name": "UserName3"}],
  foiProgramAreaList:[],
  foiIsRequiredError:true,  
  foirequiredFields: {},

  foiSelectedRequestType: "",
  foiSelectedReceiveMode: "",
  foiSelectedDeliveryMode: "",
  foiSelectedAssignedTo: "",
  foiRequestDescription: "",
  foiStartDate:"",
  foiEndDate: "",
  foiReceivedDate: "",
  foiRequestStartDate: "",
  foiIsMinistrySelected: false,
}

/*{"applicantcategoryid": 0, "name": "Select Category"},{"applicantcategoryid": 1, "name": "Business", "description": "Business", "isactive": true}, {"applicantcategoryid": 2,
  "name": "Individual", "description": "Individual", "isactive": true}, {"applicantcategoryid": 3, "name": "Interest Group", "description": "Interest Group", "isactive": true}, {"applicantcategoryid": 4, "name": "Law Firm",
  "description": "Law Firm", "isactive": true}, {"applicantcategoryid": 5, "name": "Media", "description": "Media",
  "isactive": true}, {"applicantcategoryid": 6, "name": "Political Party", "description": "Political Party", "isactive":
  true}, {"applicantcategoryid": 7, "name": "Political Party", "description": "Political Party", "isactive": true},
  {"applicantcategoryid": 8, "name": "Researcher", "description": "Researcher", "isactive": true}, {"applicantcategoryid":
  9, "name": "Other Governments", "description": "Other Governments", "isactive": true}, {"applicantcategoryid": 10,
  "name": "Other Public Body", "description": "Other Public Body", "isactive": true} */

const foiRequests = (state = initialState, action)=> {  
  switch (action.type) {
    case FOI_ACTION_CONSTANTS.IS_LOADING:
      return {...state, isLoading: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_LIST_REQUESTS:
      return {...state, foiRequestsList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_REQUESTS_COUNT:
      return {...state, foiRequestsCount: action.payload.count};
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DETAIL:
      const foiRequiredFieldsList = ["assignedTo","category","requestType", "receivedMode", "deliveryMode", "startDate", "endDate", "receivedDateUF","description","selectedMinistries"];
      const newState = state;      
      newState.foiRequestDetail = action.payload;
      var requiredFiledswithData = {};
      foiRequiredFieldsList.map(field => requiredFiledswithData[field] = newState.foiRequestDetail[field])
      // console.log(`requiredFiledswithData = ${JSON.stringify(requiredFiledswithData)}`);
      newState.foirequiredFields = requiredFiledswithData;
      newState.foiSelectedRequestType = newState.foiRequestDetail.requestType;
      newState.foiSelectedAssignedTo = newState.foiRequestDetail.assignedTo;
      newState.foiRequestDescription = newState.foiRequestDetail.description;
      newState.foiStartDate = newState.foiRequestDetail.fromDate;
      newState.foiEndDate = newState.foiRequestDetail.fromDate;
      const formattedReceivedDate = newState.foiRequestDetail.receivedDateUF;
      newState.foiReceivedDate = formattedReceivedDate;
      newState.foiRequestStartDate = formattedReceivedDate;
      return {...state, foiRequestDetail: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_IS_REQUEST_UPDATING:
      return {...state, foiIsRequestUpdating: action.payload};
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
    // case FOI_ACTION_CONSTANTS.FOI_COUNTRYLIST:
    //     return {...state, foiCountryList: action.payload};  
    // case FOI_ACTION_CONSTANTS.FOI_PROVINCELIST:
    //     return {...state, foiProvinceList: action.payload};
    // case FOI_ACTION_CONSTANTS.FOI_REQUEST_TYPELIST:
    //     return {...state, foiRequestTypeList: action.payload};
    // case FOI_ACTION_CONSTANTS.FOI_RECEIVED_MODELIST:
    //     return {...state, foiReceiveModeList: action.payload};
    // case FOI_ACTION_CONSTANTS.FOI_DELIVERY_MODELIST:
    //     return {...state, foiDeliveryModeList: action.payload};
    // case FOI_ACTION_CONSTANTS.FOI_ASSIGNED_TOLIST:
    //     return {...state, foiAssignedToList: action.payload};              
    default:
      return state;
  }
}

export default foiRequests ;
