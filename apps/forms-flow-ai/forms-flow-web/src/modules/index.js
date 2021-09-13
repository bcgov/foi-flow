import { combineReducers } from "redux";
import { connectRouter } from "connected-react-router";
import user from "./userDetailReducer";
import foiRequests from  './FOI/foiRequestsReducer';

const createRootReducer = (history) =>
  combineReducers({
    user,       
    router: connectRouter(history),   
    foiRequests
  });

export default createRootReducer;
