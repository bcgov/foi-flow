import { combineReducers } from "redux";
import { connectRouter } from "connected-react-router";
import user from "./userDetailReducer";
import foiRequests from  './FOI/foiRequestsReducer';
import notifications from './FOI/foiNotificationsReducer';

const createRootReducer = (history) =>
  combineReducers({
    user,       
    router: connectRouter(history),   
    foiRequests,
    notifications
  });

export default createRootReducer;
