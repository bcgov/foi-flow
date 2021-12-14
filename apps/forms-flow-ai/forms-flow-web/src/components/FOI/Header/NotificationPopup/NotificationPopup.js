import React from "react";
import { Tabs, ListGroup, Tab, Row, Col } from "react-bootstrap";
import './notificationpopup.scss';
import NotificationList from './NotificationList/NotificationList'

const NotificationPopup = () => {

  const listItems = [1, 2, 3, 4, 5, 6, 7, 8, 9,10].map((number,index) =>
    <NotificationList key= {index} number={number}></NotificationList>
  )


  return (
    <Tabs defaultActiveKey="my-request" id="uncontrolled-tab-example" className="notification-tab">
      <Tab eventKey="my-request" title="My Requests" className="popup-background">
        <Row className="list-header">
          <Col><div><i className="fa fa-volume-up"></i></div></Col>
          <Col className="close-btn-align">
            <div className="notification-dismiss">
              <i className="fa fa-times" style={{paddingRight:"5px"}}></i>Dismiss All
            </div></Col>
        </Row>
        <ListGroup className="notification-list">
        {listItems}
        </ListGroup>
      </Tab>
      <Tab eventKey="watch-request" title="Watching Requests" className="popup-background">
        <Row className="list-header">
          <Col><div><i className="fa fa-volume-up"></i></div></Col>
          <Col className="close-btn-align">
          <div className="notification-dismiss">
            <i className="fa fa-times" style={{paddingRight:"5px"}}></i>
            Dismiss All</div></Col>
        </Row>
        <ListGroup className="notification-list">
        {listItems}
        </ListGroup>
      </Tab>

    </Tabs>
  );

}


export default NotificationPopup;