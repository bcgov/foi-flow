import {
    httpGETRequest,
    httpDELETERequest,
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
  } from "../../../actions/FOI/foiRequestActions";
  import{
    setFOINotifications,
  } from "../../../actions/FOI/foiNotificationActions"
  import UserService from "../../../services/UserService";
  import { replaceUrl } from "../../../helper/FOI/helper"; 
  import {fnDone} from './foiServicesUtil';

  
  export const fetchFOINotifications = (...rest) => {
    const done = fnDone(rest);
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_NOTIFICATIONS, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            dispatch(setFOINotifications(res.data));
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done(error);
        });
    };
  };

  export const deleteFOINotifications = (idNumber, notificationId, type, ...rest) => {
    const done = fnDone(rest);
    let apiUrl = "";
    if(type){
      apiUrl = replaceUrl(replaceUrl(
        API.FOI_DELETE_ALL_NOTIFICATIONS,
        "<type>",
        type
      ));
    }
    else{
      apiUrl = replaceUrl(replaceUrl(
        API.FOI_DELETE_NOTIFICATION,
        "<idNumber>",
        idNumber
      ), "<notificationId>", notificationId);
    }
    return (dispatch) => {
      httpDELETERequest(apiUrl, UserService.getToken())
        .then((res) => {
          dispatch(fetchFOINotifications());
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            done("Error dismissing Notification");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
          done(error);
        });
    };
  };
