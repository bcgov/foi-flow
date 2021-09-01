import { combineReducers } from "redux";
import { connectRouter } from "connected-react-router";


import user from "./userDetailReducer";


import applications from './applicationsReducer';


import foiRequests from  './FOI/foiRequestsReducer';

const createRootReducer = (history) =>
  combineReducers({
    user,       
    applications,

    router: connectRouter(history),
   
    foiRequests
  });

export default createRootReducer;
