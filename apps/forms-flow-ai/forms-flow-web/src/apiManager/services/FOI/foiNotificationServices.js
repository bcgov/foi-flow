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

  
  export const fetchFOINotifications = () => {
    //const done = fnDone(rest);
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_NOTIFICATIONS, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            dispatch(setFOINotifications(res.data));
            //done(null, res.data);
          } else {
            console.log("Error", res);
            dispatch(serviceActionError(res));
          }
        })
        .catch((error) => {
          console.log("Error", error);
          dispatch(serviceActionError(error));
         // done(error);
        });
    };
  };

  export const deleteFOINotification = (idNumber, notificationId,data,) => {
    //const done = fnDone(rest);
    let apiUrl = replaceUrl(replaceUrl(
      API.FOI_DELETE_NOTIFICATION,
      "<idNumber>",
      idNumber
    ), "<notificationId>", notificationId);
    return (dispatch) => {
      httpDELETERequest(apiUrl, data)
        .then((res) => {
          dispatch(fetchFOINotifications())
          if (res.data) {
            dispatch(setFOINotifications(res.data));
            //done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
           // done("Error dismissing Notification");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
         // done(error);
        });
    };
  };

  export const deleteAllNotifications = (data) => {
    //const done = fnDone(rest);
    return (dispatch) => {
      httpDELETERequest(API.FOI_DELETE_ALL_NOTIFICATIONS, data)
        .then((res) => {
          dispatch(fetchFOINotifications())
          if (res.data) {
            //dispatch(setFOINotifications(res.data));
            //done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            //done("Error dismissing all Notifications");
          }
        })
        .catch((error) => {
          dispatch(serviceActionError(error));
         // done(error);
        });
    };
  };