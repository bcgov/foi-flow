import FOI_ACTION_CONSTANTS from "../../actions/FOI/foiActionConstants";
const initialState = {
  foiNotifications: []
}

const notifications = (state = initialState, action = {})=> {
  switch (action.type) {
    case FOI_ACTION_CONSTANTS.IS_LOADING:
      return {...state, isLoading: action.payload};
    case FOI_ACTION_CONSTANTS.FOI_NOTIFICATIONS:
      return {...state, foiNotifications: action.payload};   
    default:
      return state;
  }
}
export default notifications ;
