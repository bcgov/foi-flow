import FOI_ACTION_CONSTANTS from "../../actions/FOI/foiActionConstants";

const initialState = {
  isLoading:true,
  foiRequestsList:[],
  foiRequestsCount:0,
  foiRequestDetail: {},
  foiIsRequestUpdating:false,  
}


const foiRequests = (state = initialState, action)=> {
  switch (action.type) {
    case FOI_ACTION_CONSTANTS.IS_LOADING:
      return {...state, isLoading: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_LIST_REQUESTS:
      return {...state, foiRequestsList: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_REQUESTS_COUNT:
      return {...state, foiRequestsCount: action.payload.count};
    case FOI_ACTION_CONSTANTS.FOI_REQUEST_DETAIL:
      return {...state, foiRequestDetail: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_IS_REQUEST_UPDATING:
      return {...state, foiIsRequestUpdating: action.payload};    
    default:
      return state;
  }
}

export default foiRequests ;
