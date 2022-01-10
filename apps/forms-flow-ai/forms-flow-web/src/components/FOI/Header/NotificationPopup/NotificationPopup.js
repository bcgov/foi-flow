import React from "react";
import { Tabs, ListGroup, Tab} from "react-bootstrap";
import './notificationpopup.scss';
import NotificationList from './NotificationList/NotificationList'

const NotificationPopup = ({notifications}) => {

  const assigmentNotifications = notifications?.map((notification,index) =>
    {return notification.notificationusertype === 'Assignee' &&
      <NotificationList key= {index} notification={notification}></NotificationList>
    }
  )

  const watchNotifications = notifications?.map((notification,index) =>
    {return notification.notificationusertype === 'Watcher' &&
      <NotificationList key= {index} notification={notification}></NotificationList>
    }
  )

  return (
    <Tabs defaultActiveKey="my-request" id="uncontrolled-tab-example" className="notification-tab">
      <Tab eventKey="my-request" title="My Requests" className="popup-background">
        {(notifications || []).find(notification => notification.notificationusertype === 'Assignee') ?
        <ListGroup className="notification-list">
        {assigmentNotifications}
        </ListGroup>
        :
        <ListGroup className="notification-list empty-notifications">
        No requests
        </ListGroup>
    }
      </Tab>
      <Tab eventKey="watch-request" title="Watching Requests" className="popup-background">
        {(notifications || []).find(notification => notification.notificationusertype === 'Watcher') ?
        <ListGroup className="notification-list">
        {watchNotifications}
        </ListGroup>
        : 
        <ListGroup className="notification-list empty-notifications">
          No watching requests
        </ListGroup>
    }
      </Tab>

    </Tabs>
  );

}


export default NotificationPopup;