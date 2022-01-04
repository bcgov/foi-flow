import React from "react";
import { Tabs, ListGroup, Tab} from "react-bootstrap";
import './notificationpopup.scss';
import NotificationList from './NotificationList/NotificationList'

const NotificationPopup = ({notifications}) => {

  const listItems = notifications?.map((notification,index) =>
    <NotificationList key= {index} notification={notification}></NotificationList>
  )


  return (
    <Tabs defaultActiveKey="my-request" id="uncontrolled-tab-example" className="notification-tab">
      <Tab eventKey="my-request" title="My Requests" className="popup-background">
        {/* <Row className="list-header">
          <Col><div><i className="fa fa-volume-up"></i></div></Col>
          <Col className="close-btn-align">
            <div className="notification-dismiss">
              <i className="fa fa-times" style={{paddingRight:"5px"}}></i>Dismiss All
            </div></Col>
        </Row> */}
        {(notifications || []).find(notification => notification.notificationusertype === 'Assignee') ?
        <ListGroup className="notification-list">
        {listItems}
        </ListGroup>
        :
        <ListGroup className="notification-list empty-notifications">
        No requests
        </ListGroup>
    }
      </Tab>
      <Tab eventKey="watch-request" title="Watching Requests" className="popup-background">
        {/* <Row className="list-header">
          <Col><div><i className="fa fa-volume-up"></i></div></Col>
          <Col className="close-btn-align">
          <div className="notification-dismiss">
            <i className="fa fa-times" style={{paddingRight:"5px"}}></i>
            Dismiss All</div></Col>
        </Row> */}
        {(notifications || []).find(notification => notification.notificationusertype === 'Watcher') ?
        <ListGroup className="notification-list">
        {listItems}
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