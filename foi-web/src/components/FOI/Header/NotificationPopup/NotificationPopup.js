import React , { useEffect, useState } from "react";
import { Tabs, ListGroup, Tab, Row, Col} from "react-bootstrap";
import './notificationpopup.scss';
import NotificationList from './NotificationList/NotificationList'
import {
  deleteFOINotifications
} from "../../../../apiManager/services/FOI/foiNotificationServices";
import {useDispatch} from "react-redux";

const NotificationPopup = ({notifications, isMinistry, ministryCode}) => {

  const [myRequestTitle, setMyRequestTitle] = useState();
  const [watchingRequestTitle, setWatchingRequestTitle] = useState();
 

  useEffect(() => {     
    tabTitle();
  },[notifications]);

  const tabTitle = () =>{
    let myRequestList = notifications?.filter(x => (x.notificationusertype === 'Assignee' || x.notificationusertype === 'Comment User'));
    let watchingRequestList = notifications?.filter(x => x.notificationusertype === 'Watcher');
    setMyRequestTitle(myRequestList?.length > 0 ? "My Notifications ("+myRequestList.length+")": "My Notifications");
    setWatchingRequestTitle(watchingRequestList?.length > 0 ? "Watching Notifications ("+watchingRequestList.length+")": "Watching Notifications");
  }

  const assigmentNotifications = notifications?.map((notification,index) =>
    {return (notification.notificationusertype === 'Assignee' || notification.notificationusertype === "Comment User") &&
      <NotificationList key= {index} notification={notification} isMinistry ={isMinistry}
      ministryCode ={ministryCode}></NotificationList>
    }
  )

  const watchNotifications = notifications?.map((notification,index) =>
    {return notification.notificationusertype === 'Watcher' &&
      <NotificationList key= {index} notification={notification} isMinistry ={isMinistry}
      ministryCode ={ministryCode}></NotificationList>
    }
  )

  const checkIfNotificationExists = (type) => {
    if(type ==='assignee' && notifications.find(notification => 
      (notification.notificationusertype === 'Assignee'|| notification.notificationusertype === "Comment User"))){
        return true;
      }
    if(type ==='watcher' && notifications.find(notification => 
      notification.notificationusertype === 'Watcher')){
         return true;
    }
  }

  const dispatch = useDispatch();
  const dismissAllNotifications = (type) => {
    dispatch(deleteFOINotifications(null, null,type));
  }

  return (
    <Tabs defaultActiveKey="my-request" id="uncontrolled-tab-example" className="notification-tab">
      <Tab eventKey="my-request" title={myRequestTitle} className="popup-background">
        {checkIfNotificationExists('assignee')  && <Row className="list-header">
          <Col className="close-btn-align">
            <div className="notification-dismiss" onClick={() => dismissAllNotifications('assignee')}>
              <i className="fa fa-times" style={{paddingRight:"5px"}}></i>Dismiss All
            </div></Col>
        </Row>}
        {checkIfNotificationExists('assignee') ?
        <ListGroup className="notification-list">
        {assigmentNotifications}
        </ListGroup>
        :
        <ListGroup className="notification-list empty-notifications">
        No notifications
        </ListGroup>}
      </Tab>
      <Tab eventKey="watch-request" title={watchingRequestTitle} className="popup-background">
        {checkIfNotificationExists('watcher') && <Row className="list-header">
          <Col className="close-btn-align">
          <div className="notification-dismiss" onClick={() => dismissAllNotifications('watcher')}>
            <i className="fa fa-times" style={{paddingRight:"5px"}}></i>
            Dismiss All</div></Col>
        </Row>}
        {checkIfNotificationExists('watcher')?
        <ListGroup className="notification-list">
        {watchNotifications}
        </ListGroup>
        : 
        <ListGroup className="notification-list empty-notifications">
          No notifications
        </ListGroup>}
      </Tab>
    </Tabs>
  );

}


export default NotificationPopup;