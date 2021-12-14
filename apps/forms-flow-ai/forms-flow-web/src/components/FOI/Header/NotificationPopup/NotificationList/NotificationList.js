import React from 'react';
import { Col, Row, ListGroup } from 'react-bootstrap';
import './notificationlist.scss';

const NotificationList = () => {
//   const number = props.number;
  return(
    <ListGroup.Item>
      <Row>
        <Col>
          <h6 className="notification-heading">EDU-2021-12345</h6>
        </Col>
        <Col className="close-btn-align">
        <i className="fa fa-times"></i>
        </Col>
      </Row>
      <div style={{fontSize:"16px"}}>New Comment:
      </div>
      <div className="notification-comment">
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
      </div>
      <Row className="notification-item-footer">
        <Col>Username</Col>
        <Col>2021 Dec 06 | HH:MM AM/PM</Col>
      </Row>
    </ListGroup.Item>
  );
}


export default NotificationList;
